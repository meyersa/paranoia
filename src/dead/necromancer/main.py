# Backend API handler
# TODO: host dispatching
# TODO: host updates

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from src.lib.mongo_util import mongo_util
from src.lib.print_util import debug_print, info_print

mongo = mongo_util()
app = FastAPI()

# Update class: What to update, what is being updated, what it is being updated to
class EntityUpdate(BaseModel):
    entity: str
    type: str
    metric: str
    value: str

@app.get("/entities", response_model=list())
async def read_hosts():

    info_print("Request received on endpoint /hosts")
    hosts = None

    try:
        hosts = await mongo.get_hosts()
        debug_print(f'Hosts returned')
        print(hosts)
        if hosts is None or len(hosts) == 0:
            raise ValueError()

    except:
        return {"error": "failed to retrieve hosts from database"}

    # Values need to be converted since BSON is dumb
    for host in hosts:
        for key, value in host.items():
            if type(value) != list:
                host[key] = str(value)
                continue

    print(type(hosts))
    return hosts


@app.post("/host")
async def update_host(update: EntityUpdate): 
    info_print("Received host update")

    try: 
        host = mongo.update_host(update.entity, update.metric, update.value)
        
    except: 
        pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
