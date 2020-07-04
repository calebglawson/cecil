'''
Pydantic models for requests and responses.
'''
from typing import List
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
    entities: str = None
    favorites_count: int = None
    followers_count: int = None
    friends_count: int = None
    geo_enabled: bool = False
    has_extended_profile: bool = False
    user_id: int
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


class PaginateUser(Paginate):
    '''
    User paginator.
    '''
    users: List[User]


class BaseTweet(BaseModel):
    '''
    Base twitter post.
    '''
    created_at: datetime
    entities: str = None
    favorite_count: int
    tweet_id: int
    is_quote_status: bool
    lang: str
    possibly_sensitive: bool
    retweet_count: int
    source: str
    source_url: str
    text: str
    user_id: int
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
    favorites: List[Favorite]


class WatchlistInfo(BaseModel):
    '''
    Top level info about a watchlist.
    '''
    name: str
    watchlist_count: int
    watchword_count: int


class AddWatchword(BaseModel):
    '''
    Add a single search term to the watchlist.
    '''
    word: str


class AddUser(BaseModel):
    '''
    Add a single user.
    '''
    user_id: int
