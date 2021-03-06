'''
Where we put things that supposedly never change.
'''


class CecilConstants:
    '''
    Never changing.
    '''
    DEACTIVATED_ROLE = 0
    ADMIN_ROLE = 1
    NON_PRIVILEGED_ROLE = 2
    SECRET_KEY = "secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES = "access_token_expire_minutes"
    HASHING_ALGORITHM = "HS256"
    WL_PATH = "./watchlists"
    CONFIG_PATH = "./config.json"
    MESSAGE_PROCESSING_IN_BACKGROUND = {
        "message": "Processing request in the background"
    }
