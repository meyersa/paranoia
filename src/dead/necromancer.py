# Backend API handler
# TODO: host dispatching

import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Any
from pydantic import BaseModel
from datetime import datetime
from os import getenv
import pymongo
import json
import logging 

MONGO_URL = getenv("MONGO_URL")
MONGO_DB = getenv("MONGO_DB")
MONGO_CLIENT = pymongo.MongoClient(MONGO_URL)[MONGO_DB]

app = FastAPI()

class UpdateModel(BaseModel):
    entity: str
    type: str
    source: str
    metric: str
    value: str
    timestamp: datetime = datetime.now()

@app.post("/entity")
async def update_entity(update: UpdateModel):
    """
    Update an entity

    - Validates
    - Posts to Mongo
    """
    logging.info(f'Update received on /entity')

    if not validate_update(update): 
        logging.info(f'Update could not be validated')
        return json.dumps({"error": "Update could not be validated"})

    logging.info("Validated update")
    logging.info("Posting update to Mongo")

    if not await post_mongo_entity(update): 
        logging.info("Failed to post to MongoDB")
        return json.dumps({"error": "Update could not be posted to MongoDB"})

    logging.info("MongoDB has been updated")
    return json.dumps("success")

def validate_update(update: UpdateModel) -> bool: 
    """
    Validate an incoming Update 
    
    Inputs: 
        update: UpdateModel to be validated 
    
    Returns: 
        bool: whether it passed validation
    """
    if update is None: 
        return False 
    
    upd_dict = update.model_dump()

    if len(upd_dict) != 6: 
        return False 
    
    return True 


async def post_mongo_entity(update: UpdateModel) -> bool: 
    """
    Post Entity Update to MongoDB
    """
    logging.debug(f'Posting update to MongoDB')

    # Get Update information
    update_dict = dict(update.model_dump())
    entity = update_dict.get("entity")
    type = update_dict.get("type")
    source = update_dict.get("source")
    metric = update_dict.get("metric")
    value = update_dict.get("metric")
    timestamp = update_dict.get("timestamp")    

    # See if entity exists 
    try: 
        mongo_entity = MONGO_CLIENT["entities"].find_one({"entity": entity, "type": type}) # type: dict

        if not mongo_entity: 
            raise ValueError("Could not locate entity in Mongo")

    except Exception as e: 
        logging.exception("Error finding entity")
        return False 
    
    logging.debug(f'Found entity: {entity} in Mongo. Continuing')

    # Upload update to updates collection 
    logging.debug(f'Uploading update to update table')
    try: 
        res = MONGO_CLIENT["updates"].insert_one(update_dict)

        logging.debug(f'Successfully uploaded update')

    except Exception as e: 
        logging.exception(f'Could not post update for {entity}')
        return False 
    
    # Check to see if anything changed from entity entry/update it
    logging.debug(f'Checking if entity: {entity} has changed since last update')

    db_metrics = mongo_entity.get("metrics") # type: list

    # TODO: Revert this back to local processing and push if addition or set if change 

    # Doesn't exist
    if metric not in [s.get("metric") for s in db_metrics]:
        logging.debug(f'Metric: {metric} does not exist on entity: {entity}')

        try:
            res = MONGO_CLIENT["entities"].update_one({
                '_id': mongo_entity.get("_id")
            }, {
                "$push": {
                    "metrics": {
                        "source": source, 
                        "metric": metric, 
                        "value": value
                    }
                }
            })

            if res.modified_count != 1: 
                raise ValueError("Modified count is not greater than 1")

            logging.debug(f'Added metric: {metric} to entity: {entity}')

            return True

        except Exception as e: 
            logging.warning(f'Could not add metric')
            return False 
        
    # Check if current version is the same
    flag = False
    for db_metric in db_metrics: 
        db_metric = db_metric # type: dict 

        # Wrong metric
        if metric != db_metric.get("metric"): 
            continue 

        # Wrong source
        if source != db_metric.get("source"): 
            continue 

        # Value is already the same
        if value == db_metric.get("value"): 
            continue 

        # Value is not the same
        flag = True 
        db_metric["value"] = value

    # No change needed
    if not flag: 
        return True
        
    # Changed needed 
    try:
        logging.info(f'Updating entity: {entity} for metric: {metric}')

        res = MONGO_CLIENT["entities"].update_one({
            '_id': mongo_entity.get("_id")
        }, {
            '$set': {
                'metrics': db_metrics
            }
        })

        if res.modified_count != 1: 
            raise ValueError("Modification count not equal to 1")

        return True 
    
    except Exception as e: 
        logging.exception(f'Could not update metrics for entity: {entity}')
        return False 
    
@app.get("/entities", response_model=list())
async def get_entities(type: str = None):
    logging.info(f'Received request on endpoint "/entities"')

    # Query
    entities = None
    try:
        entities = await get_mongo_entities(type)

        if entities is None or len(entities) == 0:
            raise ValueError("No entities found")

    except Exception as e:
        logging.exception(f'Failed to query entities from Mongo')
        return {"error": "Failed to query entities from Mongo"}

    logging.debug(f'Received hosts from MongoDB')

    # Values need to be converted since BSON is dumb
    logging.debug(f'Converting response to str forced')
    entities = [str(s) for s in entities]

    logging.info(f'Returned {type} entities on /entities')

    return entities

async def get_mongo_entities(type: str = None) -> list[str]:
    """
    Get Entities from MongoDB
    
    Inputs: 
        type: str of entity type to get from Mongo
        
    Returns: 
        list: of all hosts in MongoDB
    """
    logging.info(f'Getting mongo entities for type: {type}')

    # Small processing
    type = type.strip().lower() 
    type.replace('"', '')

    if "web" in type: 
        type = "website"
        
    if "host" in type: 
        type = "host"

    logging.debug(f'Querying Mongo')

    # Type specified
    if type:
        res = [host for host in MONGO_CLIENT["entities"].find({"type": type}, projection={'_id': False, 'entity': True})]

    # No type, get al
    else:
        res = [host for host in MONGO_CLIENT["entities"].find(projection={'_id': False, 'entity': True})]

    # Get just the value 
    returnables = list() 
    for dict in res: 
        returnables.extend(dict.values())

    logging.debug(f'Found {len(returnables)} hosts in MongoDB')

    return returnables

if __name__ == "__main__":
    if MONGO_DB is None or MONGO_URL is None:
        raise ValueError("Could not locate Mongo ENV variables")

    uvicorn.run(app, host="0.0.0.0", port=8000)
