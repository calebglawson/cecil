'''
Pydantic models for requests and responses.
'''
from typing import List, Any
from datetime import datetime
from pydantic import BaseModel


class Paginate(BaseModel):
    '''
    Base class for methods returning sqlalchemy paginate objects.
    '''
    has_next: bool
    has_previous: bool
    next_page: int = None
    pages: int
    previous_page: int = None
    total: int

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True


class User(BaseModel):
    '''
    Twitter user top level data.
    '''
    contributors_enabled: bool = False
    created_at: datetime = None
    default_profile: bool = False
    default_profile_image: bool = False
    description: str = None
    entities: dict = None
    favorites_count: int = None
    followers_count: int = None
    friends_count: int = None
    geo_enabled: bool = False
    has_extended_profile: bool = False
    user_id: str
    is_translation_enabled: bool = False
    is_translator: bool = False
    lang: str = None
    listed_count: int = None
    location: str = None
    name: str = None
    needs_phone_verification: bool = None
    profile_banner_url: str = None
    profile_image_url: str = None
    protected: bool = None
    screen_name: str = None
    statuses_count: int = None
    suspended: bool = None
    url: str = None
    verified: bool = False
    last_updated: datetime = None

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True


class Tag(BaseModel):
    '''
    Embedded tag.
    '''
    tag_id: str
    text: str

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True


class BaseNote(BaseModel):
    '''
    Base model note.
    '''
    note_id: Any
    text: str
    created_at: datetime

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True


class UserNote(BaseNote):
    '''
    User note.
    '''
    pass  # pylint: disable=unnecessary-pass


class PaginateUserNotes(Paginate):
    '''
    Paginate user notes.
    '''
    items: List[UserNote]


class TweetNote(BaseNote):
    '''
    A note on a tweet.
    '''
    tweet_id: str


class UserStats(BaseModel):
    '''
    House all the  stats under one roof.
    '''
    followers_watchlist_percent: float
    followers_watchlist_completion: float
    friends_watchlist_percent: float
    friends_watchlist_completion: float
    favorite_watchlist_percent: float
    retweet_watchlist_percent: float


class PaginateUser(Paginate):
    '''
    User paginator.
    '''
    items: List[User]


class BaseTweet(BaseModel):
    '''
    Base twitter post.
    '''
    created_at: datetime
    entities: dict = None
    favorite_count: int
    tweet_id: str
    is_quote_status: bool
    lang: str
    possibly_sensitive: bool
    retweet_count: int
    source: str
    source_url: str
    text: str
    user_id: str
    screen_name: str
    name: str
    last_updated: datetime

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True


class Favorite(BaseTweet):
    '''
    A favorite is essentiallty a BaseTweet.
    '''
    pass  # pylint: disable=unnecessary-pass


class PaginateFavorites(Paginate):
    '''
    Favorite paginator.
    '''
    items: List[Favorite]


class TimelineTweet(BaseTweet):
    '''
    Timelines can have retweets.
    '''
    retweet_user_id: str = None
    retweet_screen_name: str = None
    retweet_name: str = None


class PaginateTimeline(Paginate):
    '''
    Timeline paginator.
    '''
    items: List[TimelineTweet]


class FriendsOrFollowing(BaseModel):
    '''
    Return user id at the top level, and if provided, a user object.
    '''
    user_id: str
    user: User = None

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True


class PaginateFriendsOrFollowing(Paginate):
    '''
    Show a list of followers or friends.
    '''
    items: List[FriendsOrFollowing]


class WatchlistInfo(BaseModel):
    '''
    Top level info about a watchlist.
    '''
    name: str
    watchlist_count: int
    watchword_count: int


class AddUser(BaseModel):
    '''
    Add a single user.
    '''
    user_id: str


class AddText(BaseModel):
    '''
    Simple request that accepts a singular string.
    '''
    text: str
