'''
Functions that the router consumes. We do the dirty work here.
'''
from os import listdir
from pathlib import Path
from baquet.user import Directory, User
from baquet.watchlist import Watchlist

_WL_PATH = Path("./watchlists")


def _exists(directoryname, filename):
    '''
    Test existance of a file.
    '''

    if not Path(f"./{directoryname}/{filename}.db").exists():
        raise FileNotFoundError


def _user_helper(user_id):
    _exists("users", user_id)
    return User(user_id)


def _wl_helper(watchlist_id):
    _exists("watchlists", watchlist_id)
    return Watchlist(watchlist_id)


def get_users(page, page_size):
    '''
    Get a list of users and top level info, paginated.
    '''
    directory = Directory()
    return directory.get_directory(page=page, page_size=page_size)


def add_user(user_id):
    '''
    Add a user.
    '''
    User(user_id).get_user()


def get_user(user_id):
    '''
    Get a user's top level info.
    '''
    user = _user_helper(user_id)
    return user.get_user()


def get_favorites(user_id, page, page_size, watchlist_id, watchwords_id):
    '''
    Get a user's favorites.
    '''
    user = _user_helper(user_id)
    if watchlist_id:
        watchlist_id = _wl_helper(watchlist_id)
    if watchwords_id:
        watchwords_id = _wl_helper(watchwords_id)
    return user.get_favorites(
        page, page_size, watchlist=watchlist_id, watchwords=watchwords_id
    )


def get_tags_favorites(user_id):
    '''
    Get the tags applying to one or more favorites.
    '''
    user = _user_helper(user_id)
    return user.get_tags("favorite")


def get_favorites_tagged(user_id, tag_id, page, page_size):
    '''
    Get the favorites that have this particular tag.
    '''
    user = _user_helper(user_id)
    return user.get_favorites_tagged(tag_id, page, page_size=page_size)


def get_notes_favorite(user_id, tweet_id):
    '''
    Get a favorite's notes.
    '''
    user = _user_helper(user_id)
    return user.get_notes_favorite(tweet_id)


def add_note_favorite(user_id, tweet_id, note):
    '''
    Add a note to a user's favorited tweet.
    '''
    user = _user_helper(user_id)
    user.add_note_favorite(tweet_id, note)


def remove_note_favorite(user_id, tweet_id, note_id):
    '''
    Remove a note from a user's favorite tweet.
    '''
    user = _user_helper(user_id)
    user.remove_note_favorite(tweet_id, note_id)


def get_tags_favorite(user_id, tweet_id):
    '''
    Get all the tags of a favorite.
    '''
    user = _user_helper(user_id)
    return user.get_tags_favorite(tweet_id)


def add_tag_favorite(user_id, tweet_id, tag):
    '''
    Add a tag to a user's favorited tweet.
    '''
    user = _user_helper(user_id)
    user.add_tag_favorite(tweet_id, tag)


def remove_tag_favorite(user_id, tweet_id, tag_id):
    '''
    Remove a tag from a user's favorited tweet.
    '''
    user = _user_helper(user_id)
    user.remove_tag_timeline(tweet_id, tag_id)


def get_followers(user_id, page, page_size, watchlist_id):
    '''
    Get the followers for a given user.
    If filtered, return user info for matches.
    '''

    user = _user_helper(user_id)
    if watchlist_id:
        watchlist_id = _wl_helper(watchlist_id)

    return user.get_followers(
        page=page, page_size=page_size, watchlist=watchlist_id)


def get_friends(user_id, page, page_size, watchlist_id):
    '''
    Get the friends for a given user.
    If filtered, return user info for matches.
    '''

    user = _user_helper(user_id)
    if watchlist_id:
        watchlist_id = _wl_helper(watchlist_id)

    return user.get_friends(
        page=page, page_size=page_size, watchlist=watchlist_id)


def get_notes_user(user_id, page, page_size):
    '''
    Get a user's notes.
    '''
    user = _user_helper(user_id)
    return user.get_notes_user(page=page, page_size=page_size)


def add_note_user(user_id, note):
    '''
    Add a note to a user.
    '''
    user = _user_helper(user_id)
    user.add_note_user(note)


def remove_note_user(user_id, note_id):
    '''
    Remove a note from a user.
    '''
    user = _user_helper(user_id)
    user.remove_note_user(note_id)


def get_stats(user_id, watchlist_id):
    '''
    Get a user's stats.
    '''
    user = _user_helper(user_id)
    watchlist = _wl_helper(watchlist_id)
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


def get_timeline(user_id, page, page_size, watchlist_id, watchwords_id):
    '''
    Get a user's timeline.
    '''
    user = _user_helper(user_id)
    if watchlist_id:
        watchlist_id = _wl_helper(watchlist_id)
    if watchwords_id:
        watchwords_id = _wl_helper(watchwords_id)
    return user.get_timeline(
        page, page_size, watchlist=watchlist_id, watchwords=watchwords_id
    )


def get_tags_timelines(user_id):
    '''
    Get a user's tags.
    '''
    user = _user_helper(user_id)
    return user.get_tags("timeline")


def get_timeline_tagged(user_id, tag_id, page, page_size):
    '''
    Get timeline tweets tagged.
    '''
    user = _user_helper(user_id)
    return user.get_timeline_tagged(tag_id, page, page_size)


def get_notes_timeline(user_id, tweet_id):
    '''
    Get a user's tweets.
    '''
    user = _user_helper(user_id)
    return user.get_notes_timeline(tweet_id)


def add_note_timeline(user_id, tweet_id, note):
    '''
    Add a note to a user's timeline tweet.
    '''
    user = _user_helper(user_id)
    user.add_note_timeline(tweet_id, note)


def remove_note_timeline(user_id, tweet_id, note_id):
    '''
    Remove a note from a user's timeline tweet.
    '''
    user = _user_helper(user_id)
    user.remove_note_timeline(tweet_id, note_id)


def get_tags_timeline(user_id, tweet_id):
    '''
    Get the tags on a particular timeline tweet.
    '''
    user = _user_helper(user_id)
    return user.get_tags_timeline(tweet_id)


def add_tag_timeline(user_id, tweet_id, tag):
    '''
    Add a tag to a user's timeline tweet.
    '''
    user = _user_helper(user_id)
    user.add_tag_timeline(tweet_id, tag)


def remove_tag_timeline(user_id, tweet_id, tag_id):
    '''
    Remove a tag from a user's timeline tweet.
    '''
    user = _user_helper(user_id)
    user.remove_tag_timeline(tweet_id, tag_id)


def get_watchlists():
    '''
    Get a list of watchlists in the watchlist directory.
    '''
    if _WL_PATH.exists():
        result = [fn.split(".")[0] for fn in listdir(_WL_PATH)]
    else:
        result = []

    return result


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

    return watchlist.get_watchlist_users()


def create_watchlist(watchlist_id):
    '''
    Create a watchlsit.
    '''
    Watchlist(watchlist_id)


def add_watchlist(watchlist_id, user_id):
    '''
    Add a user to the watchlist.
    '''
    watchlist = _wl_helper(watchlist_id)
    user = _user_helper(user_id)
    watchlist.add_watchlist(user)


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
    watchlist.add_watchword(watchword)
