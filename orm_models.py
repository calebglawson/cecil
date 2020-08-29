'''
This is where Cecil's users are kept.
'''

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()


class User(BASE):
    '''
    Logged in Cecil user.
    '''
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Integer, ForeignKey('roles.role_id'), nullable=False)
    invited_by = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    created_at = Column(DateTime)
    last_login = Column(DateTime, nullable=True)


class Role(BASE):
    '''
    A user's assigned role.
    '''
    __tablename__ = 'roles'
    role_id = Column(Integer, primary_key=True)
    role_name = Column(String, nullable=False)


class InviteCode(BASE):
    '''
    Admin generated invite codes.
    '''
    __tablename__ = 'invite_codes'
    invite_id = Column(Integer, primary_key=True)
    hashed_invite_code = Column(String, unique=True)
    expires_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    created_at = Column(DateTime)
