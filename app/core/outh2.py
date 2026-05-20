from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from cryptography.fernet import Fernet

# from . import access_token, models
from app.models import user as user_models

from app.core.config import settings

from app.db.base import (
    get_db, 
    SessionLocal
)


from app.utils.logger import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')
fernet = Fernet(settings.ENCRYPTION_KEY)


# def get_current_user(token: str= Depends(oauth2_scheme)):
#     credential_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED, 
#         detail='Could not validate credentials',
#         headers={"WWW-Authenticate": "Bearer"}
#     )
#     return access_token.verify_token(token, credential_exception)
    
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session =Depends(get_db)
)-> user_models.User:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decrypt_token = fernet.decrypt(token.encode()).decode()
        payload = jwt.decode(decrypt_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        user = payload.get("user")
        email = user.get("email")
        user_id = user.get('user_uid')

        if not user:
            raise cred_exc
    except JWTError:
        raise cred_exc
    user = db.query(user_models.User).filter(user_models.User.email == email,
                                             user_models.User.id==user_id).first()

    if not user:
        raise cred_exc
    return user


def require_role(*roles:str):
    """
    Docstring for require_role
    
    :param roles: only owner and admin get acccess to some features
    :type roles: str
    Usege: Depends(require_role("admin", "owner"))
    """
    def dependency(current_user: user_models.User = Depends(get_current_user)):
        db = SessionLocal()
        role = db.query(user_models.UserInformation.role).filter(user_models.UserInformation.id==current_user.user_id).first()
        logging.info(f"Trying to access the user {current_user} and role: {role[0]}")

        if role[0] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Insufficient Role'
            )
        return current_user
    return dependency


def get_current_token(token:str = Depends(oauth2_scheme)):
    return token

