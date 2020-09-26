'''
This module routes all watchlist operations.
'''

from os import listdir
from typing import List
from fastapi import APIRouter
from baquet.watchlist import Watchlist

import helpers
import json_models

ROUTER = APIRouter()


@ROUTER.get("/", response_model=List[str])
async def get_watchlists():
    '''
    Get a list of watchlists in the watchlist directory.
    '''
    if helpers.wl_path().exists():
        result = [fn.split(".")[0] for fn in listdir(helpers.wl_path())]
    else:
        result = []

    return result


@ROUTER.post("/")
async def add_watchlist(
        watchlist: json_models.AddWatchlist,
):
    '''
    Create a watchlist.
    '''
    Watchlist(watchlist.watchlist_id)


@ROUTER.get("/{watchlist_id}", response_model=json_models.WatchlistInfo)
async def get_watchlist(
        watchlist_id: str,
):
    '''
    Get top level details of a watchlist.
    '''
    watchlist = helpers.wl_getter(watchlist_id)

    return {
        'name': watchlist_id,
        'watchlist_count': watchlist.get_watchlist_count(),
        'watchword_count': watchlist.get_watchwords_count()
    }


@ROUTER.get("/{watchlist_id}/users/", response_model=List[json_models.User])
async def get_watchlist_users(
        watchlist_id: str,
):
    '''
    Get users on the watchlist.
    '''
    watchlist = helpers.wl_getter(watchlist_id)
    watchlist.refresh_watchlist_user_data()

    return watchlist.get_watchlist_users()


@ROUTER.post("/{watchlist_id/import/blockbot/")
async def import_blockbot_list(
        watchlist_id: str,
        import_details: json_models.ImportBlockbotList,
):
    '''
    Import a blockbot list.
    '''
    watchlist = helpers.wl_getter(watchlist_id)
    watchlist.import_blockbot_list(
        import_details.blockbot_id,
        import_details.name
    )


@ROUTER.post("/{watchlist_id}/import/twitter/")
async def import_twitter_list(
        watchlist_id: str,
        import_details: json_models.ImportTwitterList,
):
    '''
    Import a twitter list.
    '''
    watchlist = helpers.wl_getter(watchlist_id)

    if import_details.twitter_id:
        import_details.slug = None
        import_details.owner_screen_name = None

    watchlist.import_twitter_list(
        twitter_id=import_details.twitter_id,
        slug=import_details.slug,
        owner_screen_name=import_details.owner_screen_name
    )


@ROUTER.get("/{watchlist_id}/sublists/", response_model=List[json_models.Sublist])
async def get_sublists(
        watchlist_id: str,
):
    '''
    Get a list of the sublists.
    '''
    watchlist = helpers.wl_getter(watchlist_id)
    return watchlist.get_sublists()


@ROUTER.get(
    "/{watchlist_id}/sublists/{sublist_id}/users/",
    response_model=List[json_models.User]
)
async def get_sublist_users(
        watchlist_id: str,
        sublist_id: str,
):
    '''
    Get the users in the sublist.
    '''
    watchlist = helpers.wl_getter(watchlist_id)
    return watchlist.get_sublist_users(sublist_id)


@ROUTER.post("/{watchlist_id}/sublists/{sublist_id}/refresh/")
async def refresh_sublist(
        watchlist_id: str,
        sublist_id: str,
):
    '''
    Refresh a sublist.
    '''
    watchlist = helpers.wl_getter(watchlist_id)
    watchlist.refresh_sublist(sublist_id)


@ROUTER.delete("/{watchlist_id}/sublists/{sublist_id}")
async def remove_sublist(
        watchlist_id: str,
        sublist_id: str,
):
    '''
    Remove a sublist.
    '''
    watchlist = helpers.wl_getter(watchlist_id)
    watchlist.remove_sublist(sublist_id)


@ROUTER.get(
    "/{watchlist_id}/sublists/{sublist_id}/exclusions/",
    response_model=List[json_models.User]
)
async def get_sublist_exclusions(
        watchlist_id: str,
        sublist_id: str,
):
    '''
    Get users that are excluded internally.
    '''
    watchlist = helpers.wl_getter(watchlist_id)
    return watchlist.get_sublist_user_exclusions(sublist_id)


@ROUTER.post("/{watchlist_id}/sublists/{sublist_id}/exclusions/{user_id}")
async def set_exclusion_status(
        watchlist_id: str,
        sublist_id: str,
        user_id: str,
        exclusion_details: json_models.ExcludeUser,
):
    '''
    Set the exclusion status of a user from a particular sublist.
    '''
    watchlist = helpers.wl_getter(watchlist_id)
    watchlist.set_user_sublist_exclusion_status(
        user_id,
        sublist_id,
        exclusion_details.excluded
    )


@ROUTER.post("/{watchlist_id}/users/")
async def add_watchlist_users(
        watchlist_id: str,
        user: json_models.AddUser,
):
    '''
    Add user to the watchlist.
    '''
    watchlist = helpers.wl_getter(watchlist_id)
    watchlist.add_watchlist(user.user_id)


@ROUTER.delete("/{watchlist_id}/users/{user_id}")
async def remove_watchlist_user(
        watchlist_id: str,
        user_id: str,
):
    '''
    Remove a user from the watchlist.
    '''
    watchlist = helpers.wl_getter(watchlist_id)
    watchlist.remove_watchlist(user_id)


@ROUTER.get("/{watchlist_id}/words/", response_model=List[str])
async def get_watchwords(
        watchlist_id: str,
):
    '''
    Get watchwords.
    '''
    watchlist = helpers.wl_getter(watchlist_id)
    return watchlist.get_watchwords()


@ROUTER.post("/{watchlist_id}/words/")
async def add_watchword(
        watchlist_id: str,
        watchword: json_models.AddText,
):
    '''
    Add a search term to the watchwords.
    '''
    watchlist = helpers.wl_getter(watchlist_id)
    watchlist.add_watchword(watchword.text)


@ROUTER.delete("/{watchlist_id}/words/")
async def remove_watchword(
        watchlist_id: str,
        watchword: json_models.AddText,
):
    '''
    Remove a watchword from the list.
    '''
    watchlist = helpers.wl_getter(watchlist_id)
    watchlist.remove_watchword(watchword.text)
