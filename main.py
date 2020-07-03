'''
Main file of the FastAPI application, routes live here.
'''

from typing import List
from fastapi import FastAPI, HTTPException
import control
from models import User, WatchlistInfo, AddWatchword, AddUser


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
    try:
        response = control.get_user(user_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'User, {user_id}, does not exist.')

    return response


@APP.post("/users/")
async def add_user(user: AddUser):
    '''
    Add a user to the directory.
    '''
    control.add_user(user.user_id)


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
    try:
        response = control.get_watchlist(watchlist_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'Watchlist, {watchlist_name}, does not exist.')

    return response


@APP.get("/watchlists/{watchlist_name}/users/", response_model=List[User])
async def get_watchlist_users(watchlist_name: str):
    '''
    Get users on the watchlist.
    '''
    try:
        response = control.get_watchlist_users(watchlist_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'Watchlist, {watchlist_name}, does not exist.')

    return response


@APP.post("/watchlists/{watchlist_name}/users/")
async def add_watchlist_users(watchlist_name: str, user: AddUser):
    '''
    Add user to the watchlist.
    '''
    try:
        control.add_watchlist(watchlist_name, user.user_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'Watchlist, {watchlist_name}, does not exist.')


@APP.get("/watchlists/{watchlist_name}/words/", response_model=List[str])
async def get_watchwords(watchlist_name: str):
    '''
    Get watchwords.
    '''
    try:
        response = control.get_watchwords(watchlist_name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'Watchlist, {watchlist_name}, does not exist.')

    return response


@APP.post("/watchlists/{watchlist_name}/words/")
async def add_watchword(watchlist_name: str, watchword: AddWatchword):
    '''
    Add a search term to the watchwords.
    '''
    try:
        control.add_watchword(watchlist_name, watchword)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'Watchlist, {watchlist_name}, does not exist.')
