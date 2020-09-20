'''
Cecil, it all starts here.
'''
import json
from os import listdir
from datetime import datetime, timedelta
from typing import List
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from baquet.user import Directory, User
from baquet.watchlist import Watchlist

import orm_models
import json_models
from constants import CecilConstants


CECIL = FastAPI()

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="token")

_WL_PATH = Path("./watchlists")


def _exists(directoryname, filename):
    '''
    Test existance of a file.
    '''

    try:
        if not Path(f"./{directoryname}/{filename}.db").exists():
            raise FileNotFoundError
    except FileExistsError:
        raise HTTPException(
            status_code=404,
            detail=f'{directoryname[0].upper() + directoryname[1:-1]}: {filename}, does not exist.'
        )


def _user_helper(user_id):
    _exists("users", user_id)
    return User(user_id)


def _wl_helper(watchlist_id):
    _exists("watchlists", watchlist_id)
    return Watchlist(watchlist_id)


def _make_config():
    config = open(Path('./config.json'))
    return json.load(config)


def _init_roles(session):
    deactivated = orm_models.Role(
        role_id=CecilConstants.DEACTIVATED_ROLE, role_name="deactivated")
    admin = orm_models.Role(
        role_id=CecilConstants.ADMIN_ROLE, role_name="admin")
    non_privileged = orm_models.Role(
        role_id=CecilConstants.NON_PRIVILEGED_ROLE, role_name="non-privileged")

    roles = [deactivated, admin, non_privileged]
    for role in roles:
        session.add(role)
    session.commit()


def _init_admin(session):
    admin = orm_models.User(
        username="admin",
        hashed_password=PWD_CONTEXT.hash("password"),
        role=CecilConstants.ADMIN_ROLE,
        created_at=datetime.utcnow(),
    )

    session.add(admin)
    session.commit()


def _init_db(database, engine, session):
    database.parent.mkdir(parents=True, exist_ok=True)
    orm_models.BASE.metadata.create_all(engine)

    _init_roles(session)
    _init_admin(session)


def _make_conn():
    database = Path(f'./cecil.db')
    engine = create_engine(
        f'sqlite:///{database}', connect_args={"check_same_thread": False})
    session = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)()

    if not database.exists():
        _init_db(database, engine, session)

    return session


def verify_password(plain_password, hashed_password):
    '''
    Verify the provided password matches the stored hash.
    '''
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password):
    '''
    Generate the password hash.
    '''
    return PWD_CONTEXT.hash(password)


def get_authuser(username: str):
    '''
    Get the user from the cecil DB for authentication.
    '''
    return CONN.query(orm_models.User).filter(orm_models.User.username == username).first()


def authenticate_user(username: str, password: str):
    '''
    Authenticate the user.
    '''
    user = get_authuser(username)
    if not user:
        return False
    if user.role == CecilConstants.DEACTIVATED_ROLE:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    '''
    Create an access token for session access.
    '''
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + \
            timedelta(minutes=CONFIG.get(
                CecilConstants.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, CONFIG.get(
        CecilConstants.SECRET_KEY), algorithm=CecilConstants.HASHING_ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(OAUTH2_SCHEME)):
    '''
    Get the current user with JWT token.
    '''
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, CONFIG.get(
            CecilConstants.SECRET_KEY), algorithms=[CecilConstants.HASHING_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = json_models.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_authuser(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: json_models.AuthUser = Depends(get_current_user)):
    '''
    Get the current user and ensure they are active.
    '''
    if current_user.role == 0:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
        current_user: json_models.AuthUser = Depends(get_current_active_user)
):
    '''
    Get the current user, ensure they are active and an admin.
    '''
    if current_user.role != CecilConstants.ADMIN_ROLE:
        raise HTTPException(status_code=401, detail="User lacks privilege")
    return current_user

CONFIG = _make_config()
CONN = _make_conn()

# CECIL USER OPERATIONS


@CECIL.get("/admin/invite_codes/", response_model=List[json_models.InviteCode])
async def get_invite_codes(
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_admin_user
        )
):
    '''
    List the created invite codes.
    '''
    return CONN.query(orm_models.InviteCode).all()


@CECIL.post("/admin/invite_codes/")
async def post_invite_code(
        invite_c: json_models.AddText,
        current_user: json_models.AuthUser = Depends(get_current_admin_user)
):
    '''
    Generate an invite code to create new users.
    '''
    invite_code_hash = PWD_CONTEXT.hash(invite_c.text)
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
    CONN.add(invite)
    CONN.commit()


@CECIL.get("/admin/users/", response_model=List[json_models.AuthUser])
async def get_authusers(
        current_user=Depends(  # pylint: disable=unused-argument
            get_current_admin_user)
):
    '''
    Get all cecil users.
    '''
    return CONN.query(orm_models.User).all()


@CECIL.post("/admin/users/{user_id}/deactivate")
async def deactivate_user(
        user_id: int,
        current_user=Depends(  # pylint: disable=unused-argument
            get_current_admin_user)
):
    '''
    Deactivate a specific user.
    '''
    user = CONN.query(orm_models.User).filter(
        orm_models.User.user_id == user_id)
    user.role = CecilConstants.DEACTIVATED_ROLE
    CONN.commit()


@CECIL.delete("/admin/invite_codes/{invite_code_id}")
async def delete_invite_code(
        invite_code_id: int,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_admin_user
        )
):
    '''
    Delete an invite code manually.
    '''
    invite_code = CONN.query(orm_models.InviteCode).filter(
        orm_models.InviteCode.invite_id == invite_code_id
    ).first()
    CONN.delete(invite_code)
    CONN.commit()


@CECIL.post("/register")
async def register(registration_data: json_models.RegistrationData):
    '''
    Register with an invite code.
    '''
    invite_codes = CONN.query(orm_models.InviteCode).all()
    invited = False
    for invite in invite_codes:
        if verify_password(registration_data.invite_code, invite.hashed_invite_code):
            invited = True
            chosen = invite

    if invited:
        new_user = orm_models.User(
            username=registration_data.username,
            hashed_password=get_password_hash(registration_data.password),
            role=CecilConstants.NON_PRIVILEGED_ROLE,
            invited_by=chosen.created_by,
            created_at=datetime.utcnow(),
        )
        CONN.add(new_user)
        CONN.delete(chosen)
        CONN.commit()


@CECIL.post("/token", response_model=json_models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    '''
    Get a token for access after logging in.
    '''
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=CONFIG.get(
        CecilConstants.ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@CECIL.post("/update_password/")
async def update_password(
        update_password_request: json_models.UpdatePassword,
        current_user: json_models.AuthUser = Depends(
            get_current_active_user
        )
):
    '''
    Update your password.
    '''
    if not update_password_request.new_password == update_password_request.confirm_new_password:
        raise HTTPException(
            status_code=400, detail="New password and confirmed password do not match.")

    authuser = authenticate_user(
        current_user.username, update_password_request.old_password)

    if authuser:
        user = get_authuser(current_user.username)
        user.hashed_password = PWD_CONTEXT.hash(
            update_password_request.new_password)
        CONN.commit()
    else:
        raise HTTPException(
            status_code=401, detail="Current password does not match.")

# TWITTER OPERATIONS


@CECIL.get("/users/", response_model=json_models.PaginateUser)
async def get_users(
        page: int = 1,
        page_size: int = 20,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get a list of users and top level info in the user directory.
    '''
    directory = Directory()
    return directory.get_directory(page=page, page_size=page_size)


@CECIL.post("/users/")
async def add_user(
        user: json_models.AddUser,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Add a user to the directory.
    '''
    User(user.user_id).get_user()


@CECIL.get("/users/{user_id}", response_model=json_models.User)
async def get_user(
        user_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get a user's top level info.
    '''
    user = _user_helper(user_id)
    return user.get_user()


@CECIL.get("/users/{user_id}/favorites/", response_model=json_models.PaginateFavorites)
async def get_favorites(
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        watchlist_id: str = None,
        watchwords_id: str = None,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get a user's favorites.
    '''
    user = _user_helper(user_id)
    if watchlist_id:
        watchlist_id = _wl_helper(watchlist_id)
    if watchwords_id:
        watchwords_id = _wl_helper(watchwords_id)
    return user.get_favorites(
        page=page,
        page_size=page_size,
        watchlist=watchlist_id,
        watchwords=watchwords_id
    )


@CECIL.get("/users/{user_id}/favorites/tags", response_model=List[json_models.Tag])
async def get_tags_favorites(
        user_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get a list of tags that apply to one or more of a user's favorites.
    '''
    user = _user_helper(user_id)
    return user.get_tags("favorite")


@CECIL.get("/users/{user_id}/favorites/tags/{tag_id}", response_model=json_models.PaginateFavorites)
async def get_favorites_tagged(
        user_id: str,
        tag_id: int,
        page: int = 1,
        page_size: int = 20,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get a list of favorites that have this particular tag.
    '''
    user = _user_helper(user_id)
    return user.get_favorites_tagged(tag_id, page, page_size=page_size)


@CECIL.get("/users/{user_id}/favorite/{tweet_id}/notes/")
async def get_notes_favorite(
        user_id: str,
        tweet_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get a list of notes on a particular tweet.
    '''
    user = _user_helper(user_id)
    return user.get_notes_favorite(tweet_id)


@CECIL.post("/users/{user_id}/favorite/{tweet_id}/notes/")
async def add_note_favorite(
        user_id: str,
        tweet_id: str,
        note: json_models.AddText,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Add a note to a user's timeline tweet.
    '''
    user = _user_helper(user_id)
    user.add_note_favorite(tweet_id, note.text)


@CECIL.delete("/users/{user_id}/favorite/{tweet_id}/notes/{note_id}")
async def remove_note_favorite(
        user_id: str,
        tweet_id: str,
        note_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Delete a note from user's timeline tweet.
    '''
    user = _user_helper(user_id)
    user.remove_note_favorite(tweet_id, note_id)


@CECIL.get("/users/{user_id}/favorites/{tweet_id}/tags/", response_model=List[json_models.Tag])
async def get_tags_favorite(
        user_id: str,
        tweet_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get the tags on a particular tweet.
    '''
    user = _user_helper(user_id)
    return user.get_tags_favorite(tweet_id)


@CECIL.post("/users/{user_id}/favorites/{tweet_id}/tags/")
async def add_tag_favorite(
        user_id: str,
        tweet_id: str,
        tag: json_models.AddText,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Add a tag to a user's timeline tweet.
    '''
    user = _user_helper(user_id)
    user.add_tag_favorite(tweet_id, tag.text)


@CECIL.delete("/users/{user_id}/favorites/{tweet_id}/tags/{tag_id}")
async def remove_tag_favorite(
        user_id: str,
        tweet_id: str,
        tag_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Delete a tag from user's favorite.
    '''
    user = _user_helper(user_id)
    user.remove_tag_favorite(tweet_id, tag_id)


@CECIL.get("/users/{user_id}/followers/", response_model=json_models.PaginateFriendsOrFollowing)
async def get_followers(
        user_id: str,
        page: int = 1,
        page_size: int = 1500,
        watchlist_id: str = None,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get a user's followers.
    '''
    user = _user_helper(user_id)
    if watchlist_id:
        watchlist_id = _wl_helper(watchlist_id)

    return user.get_followers(
        page=page, page_size=page_size, watchlist=watchlist_id)


@CECIL.get("/users/{user_id}/friends/", response_model=json_models.PaginateFriendsOrFollowing)
async def get_friends(
        user_id: str,
        page: int = 1,
        page_size: int = 1500,
        watchlist_id: str = None,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get a user's friends.
    '''
    user = _user_helper(user_id)
    if watchlist_id:
        watchlist_id = _wl_helper(watchlist_id)

    return user.get_friends(
        page=page, page_size=page_size, watchlist=watchlist_id)


@CECIL.get("/users/{user_id}/notes/", response_model=json_models.PaginateUserNotes)
async def get_notes_user(
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get the notes about a user.
    '''
    user = _user_helper(user_id)
    return user.get_notes_user(page=page, page_size=page_size)


@CECIL.post("/users/{user_id}/notes/")
async def add_note_user(
        user_id: str,
        note: json_models.AddText,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Add a note to a user's file.
    '''
    user = _user_helper(user_id)
    user.add_note_user(note.text)


@CECIL.delete("/users/{user_id}/notes/{note_id}")
async def remove_note_user(
        user_id: str,
        note_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Remove a note from a user's file.
    '''
    user = _user_helper(user_id)
    user.remove_note_user(note_id)


@CECIL.get("/users/{user_id}/stats/{watchlist_id}", response_model=json_models.UserStats)
async def get_stats(
        user_id: str,
        watchlist_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get a user's friends.
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


@CECIL.get("/users/{user_id}/timeline/", response_model=json_models.PaginateTimeline)
async def get_timeline(
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        watchlist_id: str = None,
        watchwords_id: str = None,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
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


@CECIL.get("/users/{user_id}/timeline/tags/")
async def get_tags_timelines(
        user_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get a timeline's tags.
    '''
    user = _user_helper(user_id)
    return user.get_tags("timeline")


@CECIL.get("/users/{user_id}/timeline/tags/{tag_id}")
async def get_timeline_tagged(
        user_id: str,
        tag_id: int,
        page: int = 1,
        page_size: int = 20,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get timelines tagged.
    '''
    user = _user_helper(user_id)
    return user.get_timeline_tagged(tag_id, page, page_size)


@CECIL.get("/users/{user_id}/timeline/{tweet_id}/notes/")
async def get_notes_timeline(
        user_id: str,
        tweet_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get timeline tweet notes.
    '''
    user = _user_helper(user_id)
    return user.get_notes_timeline(tweet_id)


@CECIL.post("/users/{user_id}/timeline/{tweet_id}/notes/")
async def add_note_timeline(
        user_id: str,
        tweet_id: str,
        note: json_models.AddText,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Add a note to a user's timeline tweet.
    '''
    user = _user_helper(user_id)
    user.add_note_timeline(tweet_id, note.text)


@CECIL.delete("/users/{user_id}/timeline/{tweet_id}/notes/{note_id}")
async def remove_note_timeline(
        user_id: str,
        tweet_id: str,
        note_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Delete a note from user's timeline tweet.
    '''
    user = _user_helper(user_id)
    user.remove_note_timeline(tweet_id, note_id)


@CECIL.get("/users/{user_id}/timeline/{tweet_id}/tags/", response_model=List[json_models.Tag])
async def get_tags_timeline(
        user_id: str,
        tweet_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get the tags on a timeline tweet.
    '''
    user = _user_helper(user_id)
    return user.get_tags_timeline(tweet_id)


@CECIL.post("/users/{user_id}/timeline/{tweet_id}/tags/")
async def add_tag_timeline(
        user_id: str,
        tweet_id: str,
        tag: json_models.AddText,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Add a tag to a user's timeline tweet.
    '''
    user = _user_helper(user_id)
    user.add_tag_timeline(tweet_id, tag.text)


@CECIL.delete("/users/{user_id}/timeline/{tweet_id}/tags/{tag_id}")
async def remove_tag_timeline(
        user_id: str,
        tweet_id: str,
        tag_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Delete a tag from user's timeline tweet.
    '''
    user = _user_helper(user_id)
    user.remove_tag_timeline(tweet_id, tag_id)


@CECIL.get("/watchlists/", response_model=List[str])
async def get_watchlists(
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get a list of watchlists in the watchlist directory.
    '''
    if _WL_PATH.exists():
        result = [fn.split(".")[0] for fn in listdir(_WL_PATH)]
    else:
        result = []

    return result


@CECIL.post("/watchlists/")
async def add_watchlist(
        watchlist: json_models.AddWatchlist,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Create a watchlist.
    '''
    Watchlist(watchlist.watchlist_id)


@CECIL.get("/watchlists/{watchlist_id}", response_model=json_models.WatchlistInfo)
async def get_watchlist(
        watchlist_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get top level details of a watchlist.
    '''
    watchlist = _wl_helper(watchlist_id)

    return {
        'name': watchlist_id,
        'watchlist_count': watchlist.get_watchlist_count(),
        'watchword_count': watchlist.get_watchwords_count()
    }


@CECIL.get("/watchlists/{watchlist_id}/users/", response_model=List[json_models.User])
async def get_watchlist_users(
        watchlist_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get users on the watchlist.
    '''
    watchlist = _wl_helper(watchlist_id)
    watchlist.refresh_watchlist_user_data()

    return watchlist.get_watchlist_users()


@CECIL.post("/watchlists/{watchlist_id/import/blockbot/")
async def import_blockbot_list(
        watchlist_id: str,
        import_details: json_models.ImportBlockbotList,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Import a blockbot list.
    '''
    watchlist = _wl_helper(watchlist_id)
    watchlist.import_blockbot_list(
        import_details.blockbot_id,
        import_details.name
    )


@CECIL.post("/watchlists/{watchlist_id}/import/twitter/")
async def import_twitter_list(
        watchlist_id: str,
        import_details: json_models.ImportTwitterList,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Import a twitter list.
    '''
    watchlist = _wl_helper(watchlist_id)

    if import_details.twitter_id:
        import_details.slug = None
        import_details.owner_screen_name = None

    watchlist.import_twitter_list(
        twitter_id=import_details.twitter_id,
        slug=import_details.slug,
        owner_screen_name=import_details.owner_screen_name
    )


@CECIL.get("/watchlists/{watchlist_id}/sublists/", response_model=List[json_models.Sublist])
async def get_sublists(
        watchlist_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get a list of the sublists.
    '''
    watchlist = _wl_helper(watchlist_id)
    return watchlist.get_sublists()


@CECIL.get("/watchlists/{watchlist_id}/sublists/{sublist_id}/users/", response_model=List[json_models.User])
async def get_sublist_users(
        watchlist_id: str,
        sublist_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get the users in the sublist.
    '''
    watchlist = _wl_helper(watchlist_id)
    return watchlist.get_sublist_users(sublist_id)


@CECIL.post("/watchlists/{watchlist_id}/sublists/{sublist_id}/refresh/")
async def refresh_sublist(
        watchlist_id: str,
        sublist_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Refresh a sublist.
    '''
    watchlist = _wl_helper(watchlist_id)
    watchlist.refresh_sublist(sublist_id)


@CECIL.delete("/watchlists/{watchlist_id}/sublists/{sublist_id}")
async def remove_sublist(
        watchlist_id: str,
        sublist_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Remove a sublist.
    '''
    watchlist = _wl_helper(watchlist_id)
    watchlist.remove_sublist(sublist_id)


@CECIL.get(
    "/watchlists/{watchlist_id}/sublists/{sublist_id}/exclusions/",
    response_model=List[json_models.User]
)
async def get_sublist_exclusions(
        watchlist_id: str,
        sublist_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    '''
    watchlist = _wl_helper(watchlist_id)
    return watchlist.get_sublist_user_exclusions(sublist_id)


@CECIL.post("/watchlists/{watchlist_id}/sublist/{sublist_id}/exclusions/{user_id}")
async def set_exclusion_status(
        watchlist_id: str,
        sublist_id: str,
        user_id: str,
        exclusion_details: json_models.ExcludeUser,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Set the exclusion status of a user from a particular sublist.
    '''
    watchlist = _wl_helper(watchlist_id)
    watchlist.set_user_sublist_exclusion_status(
        user_id,
        sublist_id,
        exclusion_details.excluded
    )


@CECIL.post("/watchlists/{watchlist_id}/users/")
async def add_watchlist_users(
        watchlist_id: str,
        user: json_models.AddUser,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Add user to the watchlist.
    '''
    watchlist = _wl_helper(watchlist_id)
    watchlist.add_watchlist(user.user_id)


@CECIL.delete("/watchlists/{watchlist_id}/users/{user_id}")
async def remove_watchlist_user(
        watchlist_id: str,
        user_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Remove a user from the watchlist.
    '''
    watchlist = _wl_helper(watchlist_id)
    watchlist.remove_watchlist(user_id)


@CECIL.get("/watchlists/{watchlist_id}/words/", response_model=List[str])
async def get_watchwords(
        watchlist_id: str,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Get watchwords.
    '''
    watchlist = _wl_helper(watchlist_id)
    return watchlist.get_watchwords()


@CECIL.post("/watchlists/{watchlist_id}/words/")
async def add_watchword(
        watchlist_id: str,
        watchword: json_models.AddText,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Add a search term to the watchwords.
    '''
    watchlist = _wl_helper(watchlist_id)
    watchlist.add_watchword(watchword.text)


@CECIL.delete("/watchlists/{watchlist_id}/words/")
async def remove_watchword(
        watchlist_id: str,
        watchword: json_models.AddText,
        current_user: json_models.AuthUser = Depends(  # pylint: disable=unused-argument
            get_current_active_user
        )
):
    '''
    Remove a watchword from the list.
    '''
    watchlist = _wl_helper(watchlist_id)
    watchlist.remove_watchword(watchword.text)
