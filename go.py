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


@CECIL.post("/users/")
async def add_user(user: models.AddUser):
    '''
    Add a user to the directory.
    '''
    control.add_user(user.user_id)


@CECIL.get("/users/{user_id}", response_model=models.User)
async def get_user(user_id: str):
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
        user_id: str,
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


@CECIL.get("/users/{user_id}/favorites/tags", response_model=List[models.Tag])
async def get_tags_favorites(
        user_id: str
):
    '''
    Get a list of tags that apply to one or more of a user's favorites.
    '''
    return control.get_tags_favorites(user_id)


@CECIL.get("/users/{user_id}/favorites/tags/{tag_id}", response_model=models.PaginateFavorites)
async def get_favorites_tagged(
        user_id: str,
        tag_id: int,
        page: int = 1,
        page_size: int = 20,
):
    '''
    Get a list of favorites that have this particular tag.
    '''
    return control.get_favorites_tagged(user_id, tag_id, page, page_size)


@CECIL.get("/users/{user_id}/favorite/{tweet_id}/notes/")
async def get_notes_favorite(
        user_id: str,
        tweet_id: str,
):
    '''
    Get a list of notes on a particular tweet.
    '''
    return control.get_notes_favorite(user_id, tweet_id)


@CECIL.post("/users/{user_id}/favorite/{tweet_id}/notes/")
async def add_note_favorite(
        user_id: str,
        tweet_id: str,
        note: models.AddText
):
    '''
    Add a note to a user's timeline tweet.
    '''
    control.add_note_favorite(user_id, tweet_id, note.text)


@CECIL.delete("/users/{user_id}/favorite/{tweet_id}/notes/{note_id}")
async def remove_note_favorite(
        user_id: str,
        tweet_id: str,
        note_id: str
):
    '''
    Delete a note from user's timeline tweet.
    '''
    control.remove_note_favorite(user_id, tweet_id, note_id)


@CECIL.get("/users/{user_id}/favorites/{tweet_id}/tags/")
async def get_tags_favorite(
        user_id: str,
        tweet_id: str
):
    '''
    Get the tags on a particular tweet.
    '''
    control.get_tags_favorite(user_id, tweet_id)


@CECIL.post("/users/{user_id}/favorites/{tweet_id}/tags/")
async def add_tag_favorite(
        user_id: str,
        tweet_id: str,
        tag: models.AddText
):
    '''
    Add a tag to a user's timeline tweet.
    '''
    control.add_tag_favorite(user_id, tweet_id, tag.text)


@CECIL.delete("/users/{user_id}/favorites/{tweet_id}/tags/{tag_id}")
async def remove_tag_favorite(
        user_id: str,
        tweet_id: str,
        tag_id: str
):
    '''
    Delete a tag from user's timeline tweet.
    '''
    control.remove_tag_favorite(user_id, tweet_id, tag_id)


@CECIL.get("/users/{user_id}/followers/", response_model=models.PaginateFriendsOrFollowing)
async def get_followers(
        user_id: str,
        page: int = 1,
        page_size: int = 1500,
        watchlist_id: str = None,
):
    '''
    Get a user's followers.
    '''
    return control.get_followers(user_id, page, page_size, watchlist_id)


@CECIL.get("/users/{user_id}/friends/", response_model=models.PaginateFriendsOrFollowing)
async def get_friends(
        user_id: str,
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


@CECIL.get("/users/{user_id}/notes/", response_model=models.PaginateUserNotes)
async def get_notes_user(user_id: str, page: int = 1, page_size: int = 20):
    '''
    Get the notes about a user.
    '''
    return control.get_notes_user(user_id, page, page_size)


@CECIL.post("/users/{user_id}/notes/")
async def add_note_user(user_id: str, note: models.AddText):
    '''
    Add a note to a user's file.
    '''
    control.add_note_user(user_id, note.text)


@CECIL.delete("/users/{user_id}/notes/{note_id}")
async def remove_note_user(user_id: str, note_id: str):
    '''
    Remove a note from a user's file.
    '''
    control.remove_note_user(user_id, note_id)


@CECIL.get("/users/{user_id}/stats/{watchlist_id}", response_model=models.UserStats)
async def get_stats(user_id: str, watchlist_id: str):
    '''
    Get a user's friends.
    '''
    try:
        response = control.get_stats(user_id, watchlist_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'User, {user_id}, does not exist.')

    return response


@CECIL.get("/users/{user_id}/timeline/", response_model=models.PaginateTimeline)
async def get_timeline(
        user_id: str,
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


@CECIL.get("/users/{user_id}/timeline/tags/")
async def get_tags_timelines(
        user_id: str
):
    '''
    Get a timeline's tags.
    '''
    return control.get_tags_timelines(user_id)


@CECIL.get("/users/{user_id}/timeline/tags/{tag_id}")
async def get_timeline_tagged(
        user_id: str,
        tag_id: str,
        page: int = 1,
        page_size: int = 20
):
    '''
    Get timelines tagged.
    '''
    return control.get_timeline_tagged(user_id, tag_id, page, page_size)


@CECIL.get("/users/{user_id}/timeline/{tweet_id}/notes/")
async def get_notes_timeline(
        user_id: str,
        tweet_id: str,
):
    '''
    Get timeline tweet notes.
    '''
    return control.get_notes_timeline(user_id, tweet_id)


@CECIL.post("/users/{user_id}/timeline/{tweet_id}/notes/")
async def add_note_timeline(
        user_id: str,
        tweet_id: str,
        note: models.AddText
):
    '''
    Add a note to a user's timeline tweet.
    '''
    control.add_note_timeline(user_id, tweet_id, note.text)


@CECIL.delete("/users/{user_id}/timeline/{tweet_id}/notes/{note_id}")
async def remove_note_timeline(
        user_id: str,
        tweet_id: str,
        note_id: str
):
    '''
    Delete a note from user's timeline tweet.
    '''
    control.remove_note_timeline(user_id, tweet_id, note_id)


@CECIL.get("/users/{user_id}/timeline/{tweet_id}/tags/")
async def get_tags_timeline(
        user_id: str,
        tweet_id: str,
):
    '''
    Get the tags on a timeline tweet.
    '''
    control.get_tags_timeline(user_id, tweet_id)


@CECIL.post("/users/{user_id}/timeline/{tweet_id}/tags/")
async def add_tag_timeline(
        user_id: str,
        tweet_id: str,
        tag: models.AddText
):
    '''
    Add a tag to a user's timeline tweet.
    '''
    control.add_tag_timeline(user_id, tweet_id, tag.text)


@CECIL.delete("/users/{user_id}/timeline/{tweet_id}/tags/{tag_id}")
async def remove_tag_timeline(
        user_id: str,
        tweet_id: str,
        tag_id: str
):
    '''
    Delete a tag from user's timeline tweet.
    '''
    control.remove_tag_timeline(user_id, tweet_id, tag_id)


@CECIL.get("/watchlists/", response_model=List[str])
async def get_watchlists():
    '''
    Get a list of watchlists in the watchlist directory.
    '''
    return control.get_watchlists()


@CECIL.post("/watchlists/")
async def add_watchlist(
        watchlist: models.AddWatchlist
):
    '''
    Create a watchlist.
    '''
    return control.create_watchlist(watchlist.watchlist_id)


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
async def add_watchword(watchlist_name: str, watchword: models.AddText):
    '''
    Add a search term to the watchwords.
    '''
    try:
        control.add_watchword(watchlist_name, watchword.text)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f'Watchlist, {watchlist_name}, does not exist.')
