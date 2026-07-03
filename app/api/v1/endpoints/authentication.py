from fastapi import APIRouter, Depends, status, HTTPException, Request, Response

from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from jose import JWTError, jwt

from datetime import datetime, timezone, timedelta


# from . import schemas, database, models, access_token

from app.core.hashing import Hash
from app.models import user as user_models
from app.models.user import UserSession, User

from app.db.base import get_db
from app.core import access_token
from app.schemas.security import (Token, 
                                  LogOut, 
                                  LogOutResponse, 
                                  TokenResponse, 
                                  RefreshTokenRequest
                        )

from app.core.outh2 import get_current_token
from app.core.access_token import create_access_token

REFRESH_TOKEN_EXPIRY = 2


router = APIRouter(
    prefix='/auth',
    tags=['authentication']
)


@router.post('/login')
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):


    user = db.query(user_models.User).filter(
        user_models.User.email == form_data.username
    ).first()

    if not user or not Hash.verify(user.password, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create tokens
    access_token, _ = create_access_token(
        data={
            'email': user.email,
            'user_uid': str(user.id)
        }
    )
    refresh_token, expire = create_access_token(
        data={
            'email': user.email,
            'user_uid': str(user.id)
        },
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
    )



    # refresh_token, expire = create_refresh_token(
    #     data={
    #         'email': user.email,
    #         'user_uid': str(user.id)
    #     }
    # )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=15 * 60,  # 15 minutes
        path="/"
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=REFRESH_TOKEN_EXPIRY * 24 * 60 * 60,  # 2 days
        path="/auth/refresh"
    )



    # Extract device info
    ip_address = request.headers.get(
        "x-forwarded-for", request.client.host
    )
    
    user_agent = request.headers.get("user-agent")

    # Create session
    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        device_name="unknown",
        device_type="unknown",
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expire,
        is_revoked=False,
        created_at=datetime.now(timezone.utc),
        last_used_at=datetime.now(timezone.utc)
    )

    db.add(session)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

 

# @router.post('/refresh-token', response_model=TokenResponse)
# def refresh_access_token(
#     request: RefreshTokenRequest,
#     db: Session = Depends(get_db)
# ):
#     """
#             Refresh Token

#             A refresh token is a long-lived authentication token used to obtain
#             a new access token after the current access token expires.

#             Access tokens are usually short-lived (e.g., 10–15 minutes) for security reasons.
#             When an access token expires, the user does not need to log in again.
#             Instead, the client sends the refresh token to the server to request
#             a new access token.

#             Purpose:
#             - Improves security by keeping access tokens short-lived.
#             - Provides a smooth user experience without frequent re-login.
#             - Allows the server to manage sessions (revoke, rotate, or invalidate tokens).

#             Security Notes:
#             - Refresh tokens should be stored securely (HTTP-only cookies or secure storage).
#             - They should have a longer expiration time than access tokens.
#             - They can be stored in the database to allow logout and session revocation.
#             - Refresh token rotation is recommended to prevent replay attacks.

#             In summary:
#             Access Token = short-term access credential.
#             Refresh Token = long-term credential used to generate new access tokens.
#         """

#     credential_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid refresh token"
#     )

#     try:
#         payload = jwt.decode(
#             request.refresh_token,
#             SECRET_KEY,
#             algorithms=[ALGORITHM]
#         )

#         user_id = payload.get("sub")

#         if not user_id:
#             raise credential_exception

#     except JWTError:
#         raise credential_exception

#     # Find session
#     session = db.query(UserSession).filter(
#         UserSession.refresh_token == request.refresh_token
#     ).first()

#     if not session:
#         raise credential_exception

#     if session.is_revoked:
#         raise credential_exception

#     if session.expires_at < datetime.now(timezone.utc):
#         raise credential_exception

#     # Rotate refresh token
#     new_refresh_token, expire = create_refresh_token(
#         data={"sub": str(user_id)}
#     )

#     session.refresh_token = new_refresh_token
#     session.expires_at = expire
#     session.last_used_at = datetime.now(timezone.utc)

#     db.commit()

#     # Create new access token
#     new_access_token = create_access_token(
#         data={"sub": str(user_id)}
#     )

#     return {
#         "access_token": new_access_token,
#         "refresh_token": new_refresh_token,
#         "token_type": "bearer"
#     }

@router.post('/logout')
def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):

    session = db.query(UserSession).filter(
        UserSession.refresh_token == request.refresh_token
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )

    session.is_revoked = True
    db.commit()

    return {
        "message": "Logged out successfully"
    }

@router.post("/logout-all")
def logout_all(current_user: User = Depends(get_current_token),
               db: Session = Depends(get_db)):

    db.query(UserSession).filter(
        UserSession.user_id == current_user.id
    ).update({"is_revoked": True})

    db.commit()

    return {"message": "Logged out from all devices"}

# POST   /auth/register
# POST   /auth/login
# POST   /auth/logout
# POST   /auth/refresh-token
# GET    /auth/me

# POST   /auth/register/patient
# POST   /auth/register/doctor
# POST   /auth/register/admin

