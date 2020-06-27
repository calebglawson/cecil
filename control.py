'''
Functions that the router consumes. We do the dirty work here.
'''
from os import listdir
from pathlib import Path
from baquet.user import Directory, User
from baquet.watchlist import Watchlist


_WL_PATH = Path("./watchlists")


def get_users(page, page_size):
    '''
    Get a list of users and top level info, paginated.
    '''
    return Directory().get(page=page, page_size=page_size).items


def get_user(user_id):
    '''
    Get a user's top level info.
    '''
    return User(user_id).get_user()


def get_watchlists():
    '''
    Get a list of watchlists in the watchlist directory.
    '''
    return [fn.split(".")[0] for fn in listdir(_WL_PATH)]


def get_watchlist(watchlist_id):
    wl = Watchlist(watchlist_id)

    return {
        'name': watchlist_id,
        'watchlist_count': wl.get_watchlist_count(),
        'watchword_count': wl.get_watchwords_count()
    }
