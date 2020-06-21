'''
Pydantic models for requests and responses.
'''

from datetime import datetime
from pydantic import BaseModel


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
