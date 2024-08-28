from souls.default import Producer
import requests
import json
import logging


class Crowdsec(Producer):
    """
    Initialize a Crowdsec Producer 

    Takes in an entity and searches it's status on Crowdsec LAPI (free one)

    Returns the metric: 
        - Status (whether banned or not)
    """

    def __init__(self, type: str, entity: str, crowdsec_lapi_url: str, crowdsec_lapi_key: str) -> None:
        """
        Create a Crowdsec Producer 

        Input: 
            entity: str to scan 
            type: str type of entity
            crowdsec_lapi_url: str of Crowdsec LAPI to connect to
            crowdsec_lapi_key: str of Crowdsec Key to use with LAPI
        """

        # Target only ipv4
        if not self.is_ip() or self.is_ipv6():
            logging.exception(f'Crowdsec Producer only supports ipv4')
            return None

        super().__init__(entity, type, "Crowdsec")

        if None in [crowdsec_lapi_key, crowdsec_lapi_url]:
            logging.exception(f'Invalid Crowdsec LAPI Key/URL')
            return None

        self._crowdsec_lapi_url = crowdsec_lapi_url
        self._crowdsec_lapi_key = crowdsec_lapi_key

        logging.info(f'Initialized Crowdsec scanner for {entity}')

        try:
            res = self.query()

            # Add to inventory
            self.add_update("Status", res)

        except:
            logging.exception(f'Unable to create update')
            return None

        logging.info(f'Finished Crowdsec producer for {entity}')

    def query(self) -> str:
        """
        Query Crowdsec for entity 
        """
        crowdsec_enrich = None
        try:
            crowdsec_enrich = requests.get(
                f"{self._crowdsec_lapi_url}v1/decisions?ip={self._entity}", headers={"X-Api-Key": self._crowdsec_lapi_key}
            )

            logging.info(f'Scanned Crowdsec successfully for {self._entity}')

            if crowdsec_enrich is None:
                raise ValueError("Did not receive a response from Crowdsec")

            if crowdsec_enrich.status_code != 200:
                raise requests.ConnectionError(f'Received status code {
                                               crowdsec_enrich.status_code}')

            if crowdsec_enrich.content == b"null":
                raise ValueError("Received invalid content")

        except:
            logging.exception(f'Failed to query Crowdsec')

        # Basically just returns blank if entity is not in "inventory"
        if len(json.loads(crowdsec_enrich.content)):
            return "Banned"

        return "Not Banned"

    def test_query(self): 
        pass 
