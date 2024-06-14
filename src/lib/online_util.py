# Verifies if a URL is online or not
import requests
import ping3 

def verify_url(url: str) -> bool: 
    """
    Takes a URL and verifies if it is reachable or not

    Input: 
        str: url to connect to 

    Returns: 
        bool: if website is reachable 

    """
    try: 
        response = requests.head(url, timeout=5)

        if response.status_code != 200: 
            raise ValueError() 
        
    except: 
        return False
    
    return True

def verify_ipv4(host_address: str) -> bool: 
    """
    Takes a URL and verifies if it is reachable or not

    Input: 
        str: url to connect to 

    Returns: 
        bool: if website is reachable 

    """
    try: 
        response = ping3.ping(host_address)

        if response is None: 
            raise ValueError()
        
    except: 
        return False
    
    return True