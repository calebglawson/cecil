'''
Cecil, it all starts here.
'''
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

import helpers
import orm_models
import json_models
import internal_users
from constants import CecilConstants
from routers import users, watchlists, admin

# INTERNAL USER OPERATIONS
@CECIL.post("/register")
async def register(registration_data: json_models.RegistrationData):
    '''
    Register with an invite code.
    '''
    with internal_users.sess() as session:
        invite_codes = session.query(orm_models.InviteCode).all()
        invited = False
        for invite in invite_codes:
            if internal_users.verify_password(
                    registration_data.invite_code,
                    invite.hashed_invite_code
            ):
                invited = True
                chosen = invite

        if invited:
            new_user = orm_models.User(
                username=registration_data.username,
                hashed_password=internal_users.get_password_hash(
                    registration_data.password),
                role=CecilConstants.NON_PRIVILEGED_ROLE,
                invited_by=chosen.created_by,
                created_at=datetime.utcnow(),
            )
            session.add(new_user)
            session.delete(chosen)
            session.commit()


@CECIL.post("/token", response_model=json_models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    '''
    Get a token for access after logging in.
    '''
    user = internal_users.authenticate_user(
        form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=CONFIG.get(
        CecilConstants.ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = internal_users.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@CECIL.post("/update_password/")
async def update_password(
        update_password_request: json_models.UpdatePassword,
        current_user: json_models.AuthUser = Depends(
            internal_users.get_current_active_user
        )
):
    '''
    Update your password.
    '''
    if not update_password_request.new_password == update_password_request.confirm_new_password:
        raise HTTPException(
            status_code=400, detail="New password and confirmed password do not match.")

    authuser = internal_users.authenticate_user(
        current_user.username, update_password_request.old_password)

    if authuser:
        with internal_users.sess() as session:
            user = internal_users.get_authuser(current_user.username)
            user.hashed_password = internal_users.PWD_CONTEXT.hash(
                update_password_request.new_password
            )
            session.merge(user)
            session.commit()
    else:
        raise HTTPException(
            status_code=401, detail="Current password does not match.")

CECIL.include_router(
    admin.ROUTER,
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(internal_users.get_current_admin_user)]
)

# TWITTER OPERATIONS

CECIL.include_router(
    users.ROUTER,
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(internal_users.get_current_active_user)]
)

CECIL.include_router(
    watchlists.ROUTER,
    prefix="/watchlists",
    tags=["Watchlists"],
    dependencies=[Depends(internal_users.get_current_active_user)]
)

CECIL = FastAPI()
CONFIG = helpers.make_config()
