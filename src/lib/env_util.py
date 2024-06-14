import os
from dotenv import load_dotenv

def get_env_variable(variable_name):
    """
    Loads the specified environment variable.

    Parameters:
        variable_name (str): The name of the environment variable to retrieve.

    Returns:
        str: The value of the specified environment variable.

    Raises:
        RuntimeError: If the specified environment variable is not found.
    """

    # Load local .env for prod
    if os.path.exists(".env"):
        load_dotenv(".env", override=True)

    # Load in the middle I guess 
    elif os.path.exists("../.env"): 
        load_dotenv("../.env", override=True)
        
    # Load root .env if dev
    elif os.path.exists("../../.env"):
        load_dotenv('../../.env', override=True)

    env_value = os.getenv(variable_name) 

    if env_value is None: 
        raise RuntimeError(f"Environment variable '{variable_name}' not found")
    
    if len(env_value) < 1: 
        raise RuntimeError(f"Environment variable '{variable_name}' not found")

    return env_value