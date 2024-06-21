# Mongo update tool
# TODO: Add comments
import pymongo 
import re 
import validators
import datetime
 
from src.lib.online_util import verify_url, verify_ipv4
from src.lib.env_util import get_env_variable
from src.lib.print_util import debug_print, info_print

class mongo_util(): 
    def __init__(self) -> None:
        # Connect to Mongo
        debug_print("Connecting to Mongo")
        mongo_client = pymongo.MongoClient(get_env_variable("MONGO_URL"))        
        debug_print("Connected to Mongo")

        # Selecting database
        mongo_database = mongo_client[get_env_variable("MONGO_DB")]
        debug_print("Connected to database")

        # Setting collections
        self.hosts_client = mongo_database["hosts"]
        self.websites_client = mongo_database["websites"]
        self.recent_client = mongo_database["recent"]
        debug_print("Connected to collections")

    def add_website(self, website_url: str) -> bool: 
        website_url = website_url.strip().lower() 

        debug_print(f'Adding website {website_url[:50]}')

        if not validators.url(website_url): 
            return False

        if not re.search("^(https?://)?([a-zA-Z0-9-]+.)+[a-zA-Z]{2,}(/)?$", website_url): 
            return False

        if len(list(self.websites_client.find_one({"uri": website_url}))) > 0: 
            return False

        debug_print(f'Website {website_url} passed validation')
        website_to_add = dict() 

        website_to_add["uri"] = website_url
        website_to_add["added"] = datetime.datetime.now()
        website_to_add["status"] = verify_url(website_url)

        res = bool(self.websites_client.insert_one(website_to_add))
        
        if res == True: 
            debug_print(f'Added {website_url} to Mongo')
            return True 
        
        debug_print(f'Website {website_url} was not added to Mongo')
        return False
    
    def get_websites(self) -> list: 
        res = list(self.websites_client.find())
        debug_print(f'Got and returned {len(res)} websites')

        return res

    def add_host(self, host_address: str) -> bool: 
        host_address = host_address.strip()

        debug_print(f'Adding host {host_address[:50]}')

        if not validators.ipv4(host_address): 
            return False
        
        if len(list(self.websites_client.find_one({"ip": host_address}))) > 0: 
            return False

        debug_print(f'Host {host_address} passed validation')
        host_to_add = dict() 

        host_to_add["ip"] = host_address
        host_to_add["added"] = datetime.datetime.now()
        host_to_add["status"] = verify_ipv4(host_address)

        res = bool(self.hosts_client.insert_one(host_address))

        if res == True: 
            debug_print(f'Added {host_address} to Mongo')
            return True 
        
        debug_print(f'Host {host_address} was not added to Mongo')
        return False            
    
    def get_hosts(self) -> list: 
        res = [host for host in self.hosts_client.find()]

        debug_print(f'Got and returned {len(res)} websites')
        print(res)
        return res
    
    def update_host(self, host, metric, value) -> bool: 
        
    # TODO: Add update area
    # TODO: trigger for recent changes / 50 maybe? or a function for each host/website