'''
Methods that are common to one or more files, to be imported willy-nilly.
'''

import json
from pathlib import Path
from fastapi import HTTPException
from baquet.user import User
from baquet.watchlist import Watchlist

from constants import CecilConstants


def _exists(directoryname, filename):
    '''
    Test existance of a file.
    '''

    try:
        if not Path(f"./{directoryname}/{filename}.db").exists():
            raise FileNotFoundError
    except FileExistsError:
        raise HTTPException(
            status_code=404,
            detail=f'{directoryname[0].upper() + directoryname[1:-1]}: {filename}, does not exist.'
        )


def user_getter(user_id):
    '''
    If the user exists, retrieve it. Otherwise throw error.
    '''
    _exists("users", user_id)
    return User(user_id)


def wl_getter(watchlist_id):
    '''
    If the watchlist exists, retrieve it. Otherwise throw error.
    '''
    _exists("watchlists", watchlist_id)
    return Watchlist(watchlist_id)


def wl_path():
    '''
    Return the path for watchlists.
    '''
    return Path(CecilConstants.WL_PATH)


def make_config():
    '''
    Open and parse config.
    '''
    config = open(Path(CecilConstants.CONFIG_PATH))
    return json.load(config)
