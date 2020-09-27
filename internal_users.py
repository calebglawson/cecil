'''
Holds methods for dealing with users internal to Cecil, i.e, users that can log in.
'''

from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

import orm_models
import json_models
from constants import CecilConstants
import helpers


PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="token")


def _init_roles(session):
    try:
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
    except:
        session.rollback()
        session.close()
        raise


def _init_admin(session):
    try:
        admin = orm_models.User(
            username="admin",
            hashed_password=PWD_CONTEXT.hash("password"),
            role=CecilConstants.ADMIN_ROLE,
            created_at=datetime.utcnow(),
        )

        session.add(admin)
        session.commit()
    except:
        session.rollback()
        session.close()
        raise


def _init_db(database, engine, session):
    session = session()
    database.parent.mkdir(parents=True, exist_ok=True)
    orm_models.BASE.metadata.create_all(engine)

    _init_roles(session)
    _init_admin(session)
    session.close()


def _make_conn():
    database = Path(f'./cecil.db')
    engine = create_engine(
        f'sqlite:///{database}', connect_args={"check_same_thread": False})
    session_factory = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)
    session = scoped_session(
        session_factory
    )

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
    with sess() as session:
        return session.query(orm_models.User).filter(orm_models.User.username == username).first()


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


@contextmanager
def sess():
    '''
    Make a managed DB to use with user management.
    '''
    session = CONN()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()


CONFIG = helpers.make_config()
CONN = _make_conn()
