'''
This module routes all user operations.
'''

from typing import List
from fastapi import APIRouter
from baquet.user import User
from baquet.directory import Directory

import json_models
import helpers

ROUTER = APIRouter()


@ROUTER.get("/", response_model=json_models.PaginateUser)
def get_users(
        page: int = 1,
        page_size: int = 20,
):
    '''
    Get a list of users and top level info in the user directory.
    '''
    directory = Directory()
    return directory.get_directory(page=page, page_size=page_size)


@ROUTER.post("/")
def add_user(
        user: json_models.AddUser,
):
    '''
    Add a user to the directory.
    '''
    User(user.user_id).get_user()


@ROUTER.get("/{user_id}/", response_model=json_models.User)
def get_user(
        user_id: str,
):
    '''
    Get a user's top level info.
    '''
    user = helpers.user_getter(user_id)
    return user.get_user()


@ROUTER.get("/{user_id}/favorites/", response_model=json_models.PaginateFavorites)
def get_favorites(
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        watchlist_id: str = None,
        watchwords_id: str = None,
):
    '''
    Get a user's favorites.
    '''
    user = helpers.user_getter(user_id)
    if watchlist_id:
        watchlist_id = helpers.wl_getter(watchlist_id)
    if watchwords_id:
        watchwords_id = helpers.wl_getter(watchwords_id)
    return user.get_favorites(
        page=page,
        page_size=page_size,
        watchlist=watchlist_id,
        watchwords=watchwords_id
    )


@ROUTER.get("/{user_id}/favorites/tags/", response_model=List[json_models.Tag])
def get_tags_favorites(
        user_id: str,
):
    '''
    Get a list of tags that apply to one or more of a user's favorites.
    '''
    user = helpers.user_getter(user_id)
    return user.get_tags("favorite")


@ROUTER.get("/{user_id}/favorites/tags/{tag_id}/", response_model=json_models.PaginateFavorites)
def get_favorites_tagged(
        user_id: str,
        tag_id: int,
        page: int = 1,
        page_size: int = 20,
):
    '''
    Get a list of favorites that have this particular tag.
    '''
    user = helpers.user_getter(user_id)
    return user.get_favorites_tagged(tag_id, page, page_size=page_size)


@ROUTER.get("/{user_id}/favorites/{tweet_id}/notes/")
def get_notes_favorite(
        user_id: str,
        tweet_id: str,
):
    '''
    Get a list of notes on a particular tweet.
    '''
    user = helpers.user_getter(user_id)
    return user.get_notes_favorite(tweet_id)


@ROUTER.post("/{user_id}/favorites/{tweet_id}/notes/")
def add_note_favorite(
        user_id: str,
        tweet_id: str,
        note: json_models.AddText,
):
    '''
    Add a note to a user's timeline tweet.
    '''
    user = helpers.user_getter(user_id)
    user.add_note_favorite(tweet_id, note.text)


@ROUTER.delete("/{user_id}/favorites/{tweet_id}/notes/{note_id}/")
def remove_note_favorite(
        user_id: str,
        tweet_id: str,
        note_id: str,
):
    '''
    Delete a note from user's timeline tweet.
    '''
    user = helpers.user_getter(user_id)
    user.remove_note_favorite(tweet_id, note_id)


@ROUTER.get("/{user_id}/favorites/{tweet_id}/tags/", response_model=List[json_models.Tag])
def get_tags_favorite(
        user_id: str,
        tweet_id: str,
):
    '''
    Get the tags on a particular tweet.
    '''
    user = helpers.user_getter(user_id)
    return user.get_tags_favorite(tweet_id)


@ROUTER.post("/{user_id}/favorites/{tweet_id}/tags/")
def add_tag_favorite(
        user_id: str,
        tweet_id: str,
        tag: json_models.AddText,
):
    '''
    Add a tag to a user's timeline tweet.
    '''
    user = helpers.user_getter(user_id)
    user.add_tag_favorite(tweet_id, tag.text)


@ROUTER.delete("/{user_id}/favorites/{tweet_id}/tags/{tag_id}/")
def remove_tag_favorite(
        user_id: str,
        tweet_id: str,
        tag_id: str,
):
    '''
    Delete a tag from user's favorite.
    '''
    user = helpers.user_getter(user_id)
    user.remove_tag_favorite(tweet_id, tag_id)


@ROUTER.get("/{user_id}/followers/", response_model=json_models.PaginateFriendsOrFollowing)
def get_followers(
        user_id: str,
        page: int = 1,
        page_size: int = 100,
        watchlist_id: str = None,
):
    '''
    Get a user's followers.
    '''
    user = helpers.user_getter(user_id)
    if watchlist_id:
        watchlist_id = helpers.wl_getter(watchlist_id)

    return user.get_followers(
        page=page, page_size=page_size, watchlist=watchlist_id)


@ROUTER.get("/{user_id}/friends/", response_model=json_models.PaginateFriendsOrFollowing)
def get_friends(
        user_id: str,
        page: int = 1,
        page_size: int = 100,
        watchlist_id: str = None,
):
    '''
    Get a user's friends.
    '''
    user = helpers.user_getter(user_id)
    if watchlist_id:
        watchlist_id = helpers.wl_getter(watchlist_id)

    return user.get_friends(
        page=page, page_size=page_size, watchlist=watchlist_id)


@ROUTER.get("/{user_id}/notes/", response_model=json_models.PaginateUserNotes)
def get_notes_user(
        user_id: str,
        page: int = 1,
        page_size: int = 20,
):
    '''
    Get the notes about a user.
    '''
    user = helpers.user_getter(user_id)
    return user.get_notes_user(page=page, page_size=page_size)


@ROUTER.post("/{user_id}/notes/")
def add_note_user(
        user_id: str,
        note: json_models.AddText,
):
    '''
    Add a note to a user's file.
    '''
    user = helpers.user_getter(user_id)
    user.add_note_user(note.text)


@ROUTER.delete("/{user_id}/notes/{note_id}/")
def remove_note_user(
        user_id: str,
        note_id: str,
):
    '''
    Remove a note from a user's file.
    '''
    user = helpers.user_getter(user_id)
    user.remove_note_user(note_id)


@ROUTER.get("/{user_id}/stats/{watchlist_id}/", response_model=json_models.UserStats)
def get_stats(
        user_id: str,
        watchlist_id: str,
):
    '''
    Get a user's friends.
    '''
    user = helpers.user_getter(user_id)
    watchlist = helpers.wl_getter(watchlist_id)
    return {
        'followers_watchlist_percent': user.get_followers_watchlist_percent(watchlist=watchlist),
        'followers_watchlist_completion': user.get_followers_watchlist_completion(
            watchlist=watchlist
        ),
        'friends_watchlist_percent': user.get_friends_watchlist_percent(watchlist=watchlist),
        'friends_watchlist_completion': user.get_friends_watchlist_completion(watchlist=watchlist),
        'favorite_watchlist_percent': user.get_favorite_watchlist_percent(watchlist=watchlist),
        'retweet_watchlist_percent': user.get_retweet_watchlist_percent(watchlist=watchlist)
    }


@ROUTER.get("/{user_id}/timeline/", response_model=json_models.PaginateTimeline)
def get_timeline(
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        watchlist_id: str = None,
        watchwords_id: str = None,
):
    '''
    Get a user's timeline.
    '''
    user = helpers.user_getter(user_id)
    if watchlist_id:
        watchlist_id = helpers.wl_getter(watchlist_id)
    if watchwords_id:
        watchwords_id = helpers.wl_getter(watchwords_id)
    return user.get_timeline(
        page, page_size, watchlist=watchlist_id, watchwords=watchwords_id
    )


@ROUTER.get("/{user_id}/timeline/tags/")
def get_tags_timelines(
        user_id: str,
):
    '''
    Get a timeline's tags.
    '''
    user = helpers.user_getter(user_id)
    return user.get_tags("timeline")


@ROUTER.get("/{user_id}/timeline/tags/{tag_id}/")
def get_timeline_tagged(
        user_id: str,
        tag_id: int,
        page: int = 1,
        page_size: int = 20,
):
    '''
    Get timelines tagged.
    '''
    user = helpers.user_getter(user_id)
    return user.get_timeline_tagged(tag_id, page, page_size)


@ROUTER.get("/{user_id}/timeline/{tweet_id}/notes/")
def get_notes_timeline(
        user_id: str,
        tweet_id: str,
):
    '''
    Get timeline tweet notes.
    '''
    user = helpers.user_getter(user_id)
    return user.get_notes_timeline(tweet_id)


@ROUTER.post("/{user_id}/timeline/{tweet_id}/notes/")
def add_note_timeline(
        user_id: str,
        tweet_id: str,
        note: json_models.AddText,
):
    '''
    Add a note to a user's timeline tweet.
    '''
    user = helpers.user_getter(user_id)
    user.add_note_timeline(tweet_id, note.text)


@ROUTER.delete("/{user_id}/timeline/{tweet_id}/notes/{note_id}/")
def remove_note_timeline(
        user_id: str,
        tweet_id: str,
        note_id: str,
):
    '''
    Delete a note from user's timeline tweet.
    '''
    user = helpers.user_getter(user_id)
    user.remove_note_timeline(tweet_id, note_id)


@ROUTER.get("/{user_id}/timeline/{tweet_id}/tags/", response_model=List[json_models.Tag])
def get_tags_timeline(
        user_id: str,
        tweet_id: str,
):
    '''
    Get the tags on a timeline tweet.
    '''
    user = helpers.user_getter(user_id)
    return user.get_tags_timeline(tweet_id)


@ROUTER.post("/{user_id}/timeline/{tweet_id}/tags/")
def add_tag_timeline(
        user_id: str,
        tweet_id: str,
        tag: json_models.AddText,
):
    '''
    Add a tag to a user's timeline tweet.
    '''
    user = helpers.user_getter(user_id)
    user.add_tag_timeline(tweet_id, tag.text)


@ROUTER.delete("/{user_id}/timeline/{tweet_id}/tags/{tag_id}/")
def remove_tag_timeline(
        user_id: str,
        tweet_id: str,
        tag_id: str,
):
    '''
    Delete a tag from user's timeline tweet.
    '''
    user = helpers.user_getter(user_id)
    user.remove_tag_timeline(tweet_id, tag_id)
