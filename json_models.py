'''
Pydantic models for requests and responses.
'''
from typing import List, Any
from datetime import datetime
from pydantic import BaseModel

# Alpha Models


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


class BaseTweet(BaseModel):
    '''
    Base twitter post.
    '''
    created_at: datetime
    entities: Any = None
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


class User(BaseModel):
    '''
    Twitter user top level data.
    '''
    contributors_enabled: bool = None
    created_at: datetime = None
    default_profile: bool = None
    default_profile_image: bool = None
    description: str = None
    entities: dict = None
    favorites_count: int = None
    followers_count: int = None
    friends_count: int = None
    geo_enabled: bool = None
    has_extended_profile: bool = None
    user_id: str
    is_translation_enabled: bool = None
    is_translator: bool = None
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
    verified: bool = None
    last_updated: datetime = None

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True

# Beta Models


class AddText(BaseModel):
    '''
    Simple request that accepts a singular string.
    '''
    text: str


class AddUser(BaseModel):
    '''
    Add a single user.
    '''
    user_id: str


class AddWatchlist(BaseModel):
    '''
    Create a watchlist.
    '''
    watchlist_id: str


class AuthUser(BaseModel):
    '''
    Authenticated user.
    '''
    user_id: int
    username: str
    role: int
    invited_by: int = None
    created_at: datetime
    last_login: datetime = None

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True


class AuthUserInDB(AuthUser):
    '''
    Authenticated user's hashed password.
    '''
    hashed_password: str


class Favorite(BaseTweet):
    '''
    A favorite is essentiallty a BaseTweet.
    '''
    pass  # pylint: disable=unnecessary-pass


class FriendsOrFollowing(BaseModel):
    '''
    Return user id at the top level, and if provided, a user object.
    '''
    user_id: str
    user: User = None

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True


class InviteCode(BaseModel):
    '''
    Used for listing invite codes, without revealing the actual codes.
    '''
    invite_id: int
    expires_at: datetime
    created_by: int
    created_at: datetime

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True


class RegistrationData(BaseModel):
    '''
    Information needed for signup.
    '''
    username: str
    password: str
    invite_code: str


class Tag(BaseModel):
    '''
    Embedded tag.
    '''
    tag_id: str
    text: str

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True


class TimelineTweet(BaseTweet):
    '''
    Timelines can have retweets.
    '''
    retweet_user_id: str = None
    retweet_screen_name: str = None
    retweet_name: str = None


class Token(BaseModel):
    '''
    Token for login.
    '''
    access_token: str
    token_type: str


class TokenData(BaseModel):
    '''
    Token data.
    '''
    username: str = None


class TweetNote(BaseNote):
    '''
    A note on a tweet.
    '''
    tweet_id: str


class UpdatePassword(BaseModel):
    '''
    Form for updating password.
    '''
    old_password: str
    new_password: str
    confirm_new_password: str


class UserNote(BaseNote):
    '''
    User note.
    '''
    pass  # pylint: disable=unnecessary-pass


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


class WatchlistInfo(BaseModel):
    '''
    Top level info about a watchlist.
    '''
    name: str
    watchlist_count: int
    watchword_count: int

# Gamma Models


class PaginateFavorites(Paginate):
    '''
    Favorite paginator.
    '''
    items: List[Favorite]


class PaginateFriendsOrFollowing(Paginate):
    '''
    Show a list of followers or friends.
    '''
    items: List[FriendsOrFollowing]


class PaginateTimeline(Paginate):
    '''
    Timeline paginator.
    '''
    items: List[TimelineTweet]


class PaginateUser(Paginate):
    '''
    User paginator.
    '''
    items: List[User]


class PaginateUserNotes(Paginate):
    '''
    Paginate user notes.
    '''
    items: List[UserNote]


class ImportBlockbotList(BaseModel):
    '''
    Details needed to import a Twitter list.
    '''
    blockbot_id: str
    name: str

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True


class ImportTwitterList(BaseModel):
    '''
    Details needed to import a Twitter list.
    '''
    twitter_id: str = None
    slug: str = None
    owner_screen_name: str = None

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True


class ExcludeUser(BaseModel):
    '''
    Whether or not to exclude a user.
    '''
    excluded: bool

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True


class Sublist(BaseModel):
    '''
    Details to view a sublist.
    '''
    sublist_id: int
    sublist_type_id: int
    name: str
    external_id: str = None

    class Config:
        '''Accept SQLAlchemy objects.'''
        orm_mode = True
