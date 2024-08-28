import logging
import datetime
import validators


class Validate():
    def _validate_input(self, input: str) -> str:
        """
        Validate an input: 
            - More than 2 characters
            - Less than 1000 characters
            - All printable characters (no carriage return)

        & Capitalizes the input

        Input: 
            str: to validate or format

        Returns: 
            str: validated

        Raises: 
            ValueError: if invalid 
        """
        input = input.strip().capitalize()

        if len(input) < 2:
            raise ValueError("Input should be more than 2 characters")

        if len(input) > 1000:
            raise ValueError("Input should be under 1000 characters")

        if not input.isprintable():
            raise ValueError("Input contains invalid characters")

        logging.debug(f'Validated input for {input}')

        return input

    def _validate_entity(self, entity: str) -> str:
        """
        Validate Endpoint & Standardize

        Endpoint can either be: 
            - ipv4
            - ipv6
            - website url

        Input: 
            entity: str to validate 

        Returns: 
            str: validated entity
        """
        entity = self._validate_input(entity).lower()

        # IPv4
        if validators.ip_address.ipv4(entity):
            return entity

        # IPv6
        if validators.ip_address.ipv6(entity):
            return entity

        # Website
        if validators.url(entity):
            return entity

        raise ValueError("Invalid entity")

    def _validate_source(self, source: str) -> str: 
        """
        Validate source against producers
        
        """
        # TODO: Validate against Producer subclasses 

        source = source.strip() 

        if len(source) > 4: 
            return source
        
        raise ValueError("Invalid source")


class Update(Validate):
    """
    Update Class 

    Used to transport an update from a soul (producer) to the database through Necromancer

    Update is type ambigous, defining required values/functions
    """

    def __init__(self, metric: str, value: str) -> None:
        """
        Create Update 

        Inputs: 
            metric: str to be updated (ie. 'Ports Open')
            value: str of metric to update to (ie. '9006, 9005, 9003') 
        """
        self._metric = self._validate_input(metric)
        self._value = self._validate_input(value)
        self._timestamp = datetime.datetime.now()

        logging.info(f'Created update for {metric} with {value}')

    def get_metric(self) -> str:
        """
        Get metric value (ie. 'Open Ports')

        Returns: 
            str: metric value
        """
        logging.debug(f'Returned metric {self._metric}')
        return self._metric

    def get_value(self) -> str:
        """
        Get uh value value (ie. '1000, 1001')

        Returns: 
            str: value value
        """
        return self._value

    def get_timestamp(self) -> datetime:
        """
        Get the timestamp

        Returns: 
            datetime: timestamp update was created at
        """
        return self._timestamp

    def get(self) -> dict:
        """
        Dictionary value of update information

        Returns: 
            dict: update information
        """
        logging.debug(f'Returned update information for {self.get_metric()}')

        return {
            "metric": self.get_metric(),
            "value": self.get_value(),
            "timestamp": self.get_timestamp()
        }

    def __str__(self) -> str:
        """
        String representation of update 

        Returns: 
            str: get() value wrapped as str
        """
        return str(self.get())


class Producer(Validate):
    def __init__(self, entity: str, type: str, source: str) -> None:
        self._entity = self._validate_entity(entity)
        self._type = self._validate_input(type)
        self._source = self._validate_source(source) 

        # To store updates in later
        self._update_list = list[Update]

        logging.info(f'Created producer update for {entity} with {type}')

    def get_entity(self) -> str:
        """
        Get the entity type

        Returns: 
            str: entity type
        """
        return self._entity

    def is_website(self) -> bool: 
        """
        Checks if the entity is a website or not
        
        Returns: 
            bool: True if it is, false if it is not
        """
        return validators.hostname(self._entity)
    
    def is_ip(self) -> bool: 
        """
        Checks if the entity is an IP (v4 or v6) or not
        
        Returns: 
            bool: True if it is, false if it is not
        """
        return not self.is_website()

    def is_ipv6(self) -> bool: 
        """
        Checks if the entity is IPv6 or not
        
        Returns: 
            bool: True if it is, false if it is not
        """
        return validators.ip_address.ipv6(self._entity)
    
    def get_type(self) -> str:
        """
        Get the type type

        Returns: 
            str: type type
        """
        return self._type

    def get_source(self) -> str: 
        """
        Get the source of the update 
        
        Returns: 
            str: name of update source 
        """
        return self._source
    
    def get_timestamp(self) -> datetime:
        return datetime.datetime.now()

    def add_update(self, metric: str, value: str) -> bool:
        """
        Add an update to a producer

        Inputs: 
            metric: str name of metric 
            value: str value of metric
        """

        # Let's make it easier to add
        if value == None:
            return False

        update = Update(metric, value)

        if update in self._update_list:
            logging.warning(
                f'A duplicated update was sent (how is this possible with timestamp)')
            return False

        logging.debug(f'Added update for {metric} on {self._entity}')

        self._update_list.append(update)
        return True

    def get_updates(self) -> list[dict]:
        """
        Get Update objects in the form to post to Necro
        
        Returns: 
            list[{
                "entity": str,
                "type": str, 
                "source": str, 
                "metric": str, 
                "value": str, 
                "timestamp": datetime
        }]"""
        updates = self._update_list
        returnables = list() 

        entity = self.get_entity() 
        type = self.get_type()
        source = self.get_source()

        for update in updates: 
            update = update # type: Update
            
            returnables.append({
                "entity": entity, 
                "type": type, 
                "source": source, 
                "metric": update.get_metric(),
                "value": update.get_value(),
                "timestamp": update.get_timestamp()
            })

        if len(returnables) < 1:
            return None 
        
        return self._update_list

    def get(self) -> dict:
        return {
            "entity": self.get_entity(),
            "type": self.get_type(),
            "updates": self.get_updates()
        }

    def __str__(self) -> str:
        """
        String representation of get value

        Returns: 
            str: get value wrapped as string
        """
        return str(self.get())