'''
Functions that the router consumes. We do the dirty work here.
'''
from os import listdir
from pathlib import Path
import json
from baquet.user import Directory, User, hydrate_user_identifiers
from baquet.watchlist import Watchlist

_WL_PATH = Path("./watchlists")


def _exists(directoryname, filename):
    '''
    Test existance of a file.
    '''

    if not Path(f"./{directoryname}/{filename}.db").exists():
        raise FileNotFoundError


def _wl_helper(watchlist_id):
    _exists("watchlists", watchlist_id)
    return Watchlist(watchlist_id)


def _user_helper(user_id):
    _exists("users", user_id)
    return User(user_id)


def _serialize_entities(item):
    if hasattr(item, "entities") and item.entities:
        item.entities = json.loads(item.entities)
    return item


def _serialize_paginated_entities(page):
    for item in page.items:
        item = _serialize_entities(item)
    return page


def get_users(page, page_size):
    '''
    Get a list of users and top level info, paginated.
    '''
    return _serialize_paginated_entities(Directory().get(page=page, page_size=page_size))


def get_user(user_id):
    '''
    Get a user's top level info.
    '''
    user = _user_helper(user_id)
    return _serialize_entities(user.get_user())


def get_favorites(user_id, page, page_size, watchlist_id, watchwords_id):
    '''
    Get a user's favorites.
    '''
    user = _user_helper(user_id)
    if watchlist_id:
        watchlist_id = _wl_helper(watchlist_id)
    if watchwords_id:
        watchwords_id = _wl_helper(watchwords_id)
    return _serialize_paginated_entities(
        user.get_favorites(
            page, page_size, watchlist=watchlist_id, watchwords=watchwords_id
        )
    )


def get_timeline(user_id, page, page_size, watchlist_id, watchwords_id):
    '''
    Get a user's timeline.
    '''
    user = _user_helper(user_id)
    if watchlist_id:
        watchlist_id = _wl_helper(watchlist_id)
    if watchwords_id:
        watchwords_id = _wl_helper(watchwords_id)
    return _serialize_paginated_entities(
        user.get_timeline(
            page, page_size, watchlist=watchlist_id, watchwords=watchwords_id
        )
    )


def get_followers(user_id, page, page_size, watchlist_id):
    '''
    Get the followers for a given user.
    If filtered, return user info for matches.
    '''

    user = _user_helper(user_id)
    if watchlist_id:
        watchlist_id = _wl_helper(watchlist_id)

    results = user.get_followers(
        page=page, page_size=page_size, watchlist=watchlist_id)

    if watchlist_id:
        user_ids = [follower.user_id for follower in results.items]
        users = hydrate_user_identifiers(user_ids=user_ids)
        new_items = []

        for item in results.items:
            new_user = {}
            for user in users:
                setattr(user, "user_id", user.id)
                if item.user_id == user.id:
                    new_user = user
            new_items.append(
                {
                    "user_id": item.user_id,
                    "user": new_user
                }
            )

        results.items = new_items

    return results


def get_friends(user_id, page, page_size, watchlist_id):
    '''
    Get the friends for a given user.
    If filtered, return user info for matches.
    '''

    user = _user_helper(user_id)
    if watchlist_id:
        watchlist_id = _wl_helper(watchlist_id)

    results = user.get_friends(
        page=page, page_size=page_size, watchlist=watchlist_id)

    if watchlist_id:
        user_ids = [friend.user_id for friend in results.items]
        users = hydrate_user_identifiers(user_ids=user_ids)
        new_items = []

        for item in results.items:
            new_user = {}
            for user in users:
                setattr(user, "user_id", user.id)
                if item.user_id == user.id:
                    new_user = user
            new_items.append(
                {
                    "user_id": item.user_id,
                    "user": new_user
                }
            )

        results.items = new_items

    return results


def get_stats(user_id, watchlist_id):
    '''
    Get a user's stats.
    '''
    user = _user_helper(user_id)
    wl = _wl_helper(watchlist_id)
    return {
        'followers_watchlist_percent': user.get_followers_watchlist_percent(watchlist=wl),
        'followers_watchlist_completion': user.get_followers_watchlist_completion(watchlist=wl),
        'friends_watchlist_percent': user.get_friends_watchlist_percent(watchlist=wl),
        'friends_watchlist_completion': user.get_friends_watchlist_completion(watchlist=wl),
        'favorite_watchlist_percent': user.get_favorite_watchlist_percent(watchlist=wl),
        'retweet_watchlist_percent': user.get_retweet_watchlist_percent(watchlist=wl)
    }


def add_user(user_id):
    '''
    Add a user.
    '''
    User(user_id)


def get_watchlists():
    '''
    Get a list of watchlists in the watchlist directory.
    '''
    return [fn.split(".")[0] for fn in listdir(_WL_PATH)]


def get_watchlist(watchlist_id):
    '''
    Get top level info about a watchlist.
    '''
    watchlist = _wl_helper(watchlist_id)

    return {
        'name': watchlist_id,
        'watchlist_count': watchlist.get_watchlist_count(),
        'watchword_count': watchlist.get_watchwords_count()
    }


def get_watchlist_users(watchlist_id):
    '''
    Get a list of users on the watchlist.
    '''
    watchlist = _wl_helper(watchlist_id)
    watchlist.refresh_watchlist_user_data()

    results = watchlist.get_watchlist_users()
    for result in results:
        result = _serialize_entities(result)
    return results


def add_watchlist(watchlist_id, user_id):
    '''
    Add a user to the watchlist.
    '''
    watchlist = _wl_helper(watchlist_id)
    watchlist.add_watchlist(user_id)


def get_watchwords(watchlist_id):
    '''
    Get the watchwords on the watchlist.
    '''
    watchlist = _wl_helper(watchlist_id)
    return watchlist.get_watchwords()


def add_watchword(watchlist_id, watchword):
    '''
    Add a search term to the watchlist.
    '''
    watchlist = _wl_helper(watchlist_id)
    watchlist.add_watchword(watchword.word)
