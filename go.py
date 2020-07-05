'''
Cecil, it all starts here.
'''

from typing import List
from fastapi import FastAPI, HTTPException
import models
import control


CECIL = FastAPI()


@CECIL.get("/users/", response_model=models.PaginateUser)
async def get_users(page: int = 1, page_size: int = 20):
    '''
    Get a list of users and top level info in the user directory.
    '''
    return control.get_users(page=page, page_size=page_size)


@CECIL.get("/users/{user_id}", response_model=models.User)
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


@CECIL.get("/users/{user_id}/favorites/", response_model=models.PaginateFavorites)
async def get_favorites(
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        watchlist_id: str = None,
        watchwords_id: str = None
):
    '''
    Get a user's favorites.
    '''
    try:
        response = control.get_favorites(
            user_id, page, page_size, watchlist_id, watchwords_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'User, {user_id}, does not exist.')

    return response


@CECIL.get("/users/{user_id}/timeline/", response_model=models.PaginateTimeline)
async def get_timeline(
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        watchlist_id: str = None,
        watchwords_id: str = None
):
    '''
    Get a user's timeline.
    '''
    try:
        response = control.get_timeline(
            user_id, page, page_size, watchlist_id, watchwords_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'User, {user_id}, does not exist.')

    return response


@CECIL.get("/users/{user_id}/followers/", response_model=models.PaginateFriendsOrFollowing)
async def get_followers(
        user_id: int,
        page: int = 1,
        page_size: int = 1500,
        watchlist_id: str = None
):
    '''
    Get a user's followers.
    '''
    try:
        response = control.get_followers(
            user_id, page, page_size, watchlist_id
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'User, {user_id}, does not exist.')

    return response


@CECIL.get("/users/{user_id}/friends/", response_model=models.PaginateFriendsOrFollowing)
async def get_friends(
        user_id: int,
        page: int = 1,
        page_size: int = 1500,
        watchlist_id: str = None
):
    '''
    Get a user's friends.
    '''
    try:
        response = control.get_friends(
            user_id, page, page_size, watchlist_id
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'User, {user_id}, does not exist.')

    return response


@CECIL.post("/users/")
async def add_user(user: models.AddUser):
    '''
    Add a user to the directory.
    '''
    control.add_user(user.user_id)


@CECIL.get("/watchlists/", response_model=List[str])
async def get_watchlists():
    '''
    Get a list of watchlists in the watchlist directory.
    '''
    return control.get_watchlists()


@CECIL.get("/watchlists/{watchlist_name}", response_model=models.WatchlistInfo)
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


@CECIL.get("/watchlists/{watchlist_name}/users/", response_model=List[models.User])
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


@CECIL.post("/watchlists/{watchlist_name}/users/")
async def add_watchlist_users(watchlist_name: str, user: models.AddUser):
    '''
    Add user to the watchlist.
    '''
    try:
        control.add_watchlist(watchlist_name, user.user_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'Watchlist, {watchlist_name}, does not exist.')


@CECIL.get("/watchlists/{watchlist_name}/words/", response_model=List[str])
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


@CECIL.post("/watchlists/{watchlist_name}/words/")
async def add_watchword(watchlist_name: str, watchword: models.AddWatchword):
    '''
    Add a search term to the watchwords.
    '''
    try:
        control.add_watchword(watchlist_name, watchword)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'Watchlist, {watchlist_name}, does not exist.')
