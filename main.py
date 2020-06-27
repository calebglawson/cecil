'''
Main file of the FastAPI application, routes live here.
'''

from typing import List
from fastapi import FastAPI
import control
from models import User, WatchlistInfo


APP = FastAPI()


@APP.get("/users/", response_model=List[User])
async def get_users(page: int = 1, page_size: int = 20):
    '''
    Get a list of users and top level info in the user directory.
    '''
    return control.get_users(page=page, page_size=page_size)


@APP.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    '''
    Get a user's top level info.
    '''
    return control.get_user(user_id)


@APP.post("/users/{user_id}", response_model=User)
async def add_user(user_id: int):
    '''
    Add a user to the directory
    '''
    return control.get_user(user_id)


@APP.get("/watchlists/", response_model=List[str])
async def get_watchlists():
    '''
    Get a list of watchlists in the watchlist directory.
    '''
    return control.get_watchlists()


@APP.get("/watchlists/{watchlist_name}", response_model=WatchlistInfo)
async def get_watchlist(watchlist_name: str):
    '''
    Get top level details of a watchlist.
    '''
    return control.get_watchlist(watchlist_name)
