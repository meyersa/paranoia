from souls.default import Producer
import nmap 
import logging 

class NMAP(Producer): 
    """
    NMAP Producer class 
    
    Takes in an entity and scans it for open ports
    
    Returns the metrics: 
        - State
        - Hostname
        - Time Elapsed
        - Device
        - Brand
        - Type
        - OS
        - Open Port Count
        - Open Ports
    """
    
    def __init__(self, type: str, entity: str) -> None:
        """
        Initialize an NMAP Producer
        
        Inputs: 
            entity: str to check     
        """
        super().__init__(entity, type, "NMAP")        
        logging.info(f'Starting NMAP producer for {entity}')

        self._nm = nmap.PortScanner()

        try: 
            self._nm.scan(entity, ports='1-60000', timeout=180)
            logging.info(f'Scanned entity {entity}')
            
            self._nm_entity = self._nm.all_hosts()[0]

            if not self._nm['nmap']['scaninfo']['error']: 
                raise nmap.PortScannerError("It said to check this key")

        except: 
            logging.exception("Could not create NMAP scanner") 
            return None
        
        # To keep track of values more easily
        update_dict = {
            "state": self.get_state(),
            "hostname": self.get_hostname(),
            "time elapsed": self.get_time(),
            "device": self.get_device(),
            "brand": self.get_brand(), 
            "type": self.get_type(),
            "os": self.get_os(),
            "open port count": self.get_port_count(),
            "open ports": self.get_ports_all()
        }

        for met, val in update_dict.items(): 
            # Final validation to try and catch None values
            if val == None: 
                logging.warning(f'Unable to get metric {met} for {entity}')
                continue
            
            # Add with handler just in case
            try: 
                self.add_update(met, val)

            except: 
                logging.exception(f'Failed to add metric {met} for {entity}')

        logging.info(f'Finished NMAP producer for {entity}')

    def get_state(self) -> str:
        """
        Get the state of the entity with NMAP
        """
        return self._nm[self._nm_entity].state()

    def get_hostname(self) -> str: 
        return self._nm[self._nm_entity].hostname()

    def get_time(self) -> str: 
        return self._nm[self._nm_entity].get("scanstats").get("elapsed")
    
    def get_device(self) -> str: 
        return self._nm[self._nm_entity].get("osmatch").get("name")
    
    def get_brand(self) -> str: 
        return self._nm[self._nm_entity].get("osmatch").get("osclass").get("vendor")
    
    def get_type(self) -> str: 
        return self._nm[self._nm_entity].get("osmatch").get("osclass").get("type")
    
    def get_os(self) -> str: 
        return self._nm[self._nm_entity].get("osmatch").get("osclass").get("osfamily")

    def get_port_count(self) -> str:
        count = 0 

        count += len(self.get_ports_ip(True))
        count += len(self.get_ports_sctp(True))
        count += len(self.get_ports_tcp(True))
        count += len(self.get_ports_udp(True))

        return count
    
    def _split_format_count(self, port_list: dict[int, dict]) -> list[str, int]: 
        """
        Private method to split a list of ports into a human readable string and count
        
        Inputs: 
            port_list: dict[int, dict] of ports
            
        Returns: 
            list[str, int]: [0] - Human readable port list, [1] - Number of ports
        """
        count = len(port_list)

        if port_list is None or count < 1: 
            return ["No open ports", 0]

        open_ports = list() 
        for port, port_info in port_list.items(): 
            state = port_info.get("state")

            # Only target open ports
            if state != "open": 
                continue

            # Don't add duplicates
            if port in open_ports: 
                continue

            # Then add to list
            open_ports.append(port)

        hum_ports = ", ".join(sorted(open_ports))
        return [hum_ports, count]

    def get_ports_ip(self, count: bool = False) -> str: 
        ports = self._nm[self._nm_entity].get("ip")

        [hum_ports, count_ports] = self._split_format_count(ports)

        if count: 
            return count_ports
        
        return hum_ports
    
    def get_ports_sctp(self, count: bool = False) -> str:
        ports = self._nm[self._nm_entity].get("sctp")

        [hum_ports, count_ports] = self._split_format_count(ports)

        if count: 
            return count_ports
        
        return hum_ports
    
    def get_ports_tcp(self, count: bool = False) -> str:
        ports = self._nm[self._nm_entity].get("tcp")

        [hum_ports, count_ports] = self._split_format_count(ports)

        if count: 
            return count_ports
        
        return hum_ports
    
    def get_ports_udp(self, count: bool = False) -> str:
        ports = self._nm[self._nm_entity].get("udp")

        [hum_ports, count_ports] = self._split_format_count(ports)

        if count: 
            return count_ports
        
        return hum_ports
    
    def get_ports_all(self, count: bool = False) -> str: 
        all_ports = list()

        all_ports.append(self.get_ports_ip())
        all_ports.append(self.get_ports_sctp())
        all_ports.append(self.get_ports_tcp())
        all_ports.append(self.get_ports_udp())

        # This is so hack but sort by port number
        j_ports = ", ".join(all_ports).split(",")
        j_ports = [int(j) for j in j_ports]

        ports = dict()
        for port in j_ports: 
            ports[port] = {"state": "open"}


        [hum_ports, count_ports] = self._split_format_count(ports)

        if count: 
            return count_ports
        
        return hum_ports