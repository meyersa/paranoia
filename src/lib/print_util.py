from src.lib.env_util import get_env_variable

def debug_print(print_line: str):
    """
    Prints debug log when env:DEBUG_PRINT is set to True
    
    Input: 
        str: print_line to be printed
    """
    print_line = print_line.strip()
    debug_flag = False

    # See if var is true, result doesn't matter since we default false
    try: 
        debug_flag = get_env_variable("DEBUG_PRINT")

    except: 
        pass 

    if debug_flag: 
        print(f'DEBUG | {print_line}')

def info_print(print_line: str): 
    """
    Prints info log when env:INFO_PRINT is set to True
    
    Input: 
        str: print_line to be printed
    """
    print_line = print_line.strip() 
    info_flag = True

    try: 
        info_flag = get_env_variable("INFO_PRINT")

    except: 
        pass

    if info_flag: 
        print(f'INFO | {print_line}')