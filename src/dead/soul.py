import logging 
import requests 

from souls.crowdsec_producer import Crowdsec
from souls.nmap_producer import NMAP

from souls.default import Producer

# TODO: Change from local
NECRO_API = "http://0.0.0.0:8000"

def get_targets(type: str) -> list[dict]: 
    """
    Get targets from Necromancer API that are of type specified

    Inputs:
        type: str of entities (e.g. website) 

    Returns: 
        list[dict] of target entities 
    """
    type = type.strip().lower()

    logging.info(f'Getting targets from Necromancer')

    try:
        res = requests.get(f'{NECRO_API}/entities?type={type}')

        if res.status_code != 200: 
            raise ValueError("Non 200 status code returned")

        targets = res.json() 

        if len(targets) < 1: 
            raise ValueError("Did not get any targets from Necromancer")

        logging.debug(f'Found {len(targets)} targets')

        return targets
    
    except Exception as e: 
        logging.exception(f'Unable to get targets from Necromancer')
        return None 
    

def get_updates(): 
    pass 

def post_updates(): 
    pass 

def main(): 
    logging.info(f'Starting SOUL Producer')

    logging.info(f'Getting targets') 
    targets = get_targets("hosts") 

    # global producers
    # producers = Producer.__subclasses__()
    
    # pretty_producers = [s.__module__.split(".")[1].capitalize() for s in producers]

    # logging.info(f'Found {len(pretty_producers)} producers: {pretty_producers}')

    pass 

if __name__ == "__main__": 
    main() 

    exit

    # CROWDSEC_LAPI_URL=
    # CROWDSEC_LAPI_KEY=
    # cs = crowdsec(CROWDSEC_LAPI_URL, CROWDSEC_LAPI_KEY) 
    # print(cs.query("177.85.247.230").get())