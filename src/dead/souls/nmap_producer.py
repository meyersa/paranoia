# TODO: finish nmap 

import nmap
from src.lib.env_util import get_env_variable

class nmap_scanner(): 
    def __init__(self): 
        pass 

def scan_host(host: str): 
    """
    Scans a given host for open ports and other network information.

    Args:
        host (str): The IP address or hostname of the target to scan.

    Returns:
        dict: A dictionary containing scan results, including elapsed time,
              timestamp, host state, and port information.
    """
    nm = nmap.PortScanner() 

    res = nm.scan(host) 
    
    nmap_info = res.get("nmap")
    scan_info = res.get("scan").get(host)

    # Packaging results
    results = dict() 

    results["elapsed_time"] = nmap_info.get("scanstats").get("elapsed")
    results["timestamp"] = nmap_info.get("scanstats").get("timestr")
    results["host_state"] = scan_info.get("status").get("state")
    results["port_info"] = scan_info.get("tcp")