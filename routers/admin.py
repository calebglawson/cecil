'''
This module routes all user operations.
'''

from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends

import internal_users
import json_models
import orm_models
import helpers
from constants import CecilConstants

ROUTER = APIRouter()


@ROUTER.get("/invite_codes/", response_model=List[json_models.InviteCode])
def get_invite_codes():
    '''
    List the created invite codes.
    '''
    with internal_users.sess() as session:
        return session.query(orm_models.InviteCode).all()


@ROUTER.post("/invite_codes/")
def post_invite_code(
        invite_c: json_models.AddText,
        current_user: json_models.AuthUser = Depends(
            internal_users.get_current_admin_user)
):
    '''
    Generate an invite code to create new users.
    '''
    invite_code_hash = internal_users.PWD_CONTEXT.hash(invite_c.text)
    created_at = datetime.utcnow()
    expires_at = created_at + \
        timedelta(minutes=CONFIG.get(
            CecilConstants.ACCESS_TOKEN_EXPIRE_MINUTES))
    invite = orm_models.InviteCode(
        hashed_invite_code=invite_code_hash,
        created_at=created_at,
        created_by=current_user.user_id,
        expires_at=expires_at,
    )
    with internal_users.sess() as session:
        session.add(invite)
        session.commit()


@ROUTER.get("/users/", response_model=List[json_models.AuthUser])
def get_authusers():
    '''
    Get all ROUTER users.
    '''
    with internal_users.sess() as session:
        return session.query(orm_models.User).all()


@ROUTER.post("/users/{user_id}/deactivate")
def deactivate_user(user_id: int):
    '''
    Deactivate a specific user.
    '''
    with internal_users.sess() as session:
        user = session.query(orm_models.User).filter(
            orm_models.User.user_id == user_id)
        user.role = CecilConstants.DEACTIVATED_ROLE
        session.commit()


@ROUTER.delete("/invite_codes/{invite_code_id}")
def delete_invite_code(invite_code_id: int):
    '''
    Delete an invite code manually.
    '''
    with internal_users.sess() as session:
        invite_code = session.query(orm_models.InviteCode).filter(
            orm_models.InviteCode.invite_id == invite_code_id
        ).first()
        session.delete(invite_code)
        session.commit()


CONFIG = helpers.make_config()
