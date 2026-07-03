from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.user import User
from app.schemas.user import (
    User as UserSchema,
    ShowUser,
    ResponseUser
)
from app.core.hashing import Hash

router = APIRouter(
    prefix='/users',
    tags=['users']
)

@router.post('/', status_code=status.HTTP_201_CREATED)
def create_user(payload:UserSchema, db:Session = Depends(get_db)):
    # Check if user with the same email already exists
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        name=payload.name,
        email=payload.email,
        password=Hash.hash(payload.password),
        dob=payload.dob,
        mobile=payload.mobile,
        gender= payload.gender,
        role=payload.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return ResponseUser(
        status="201",
        message="User created successfully",
        lang="en",
        data=ShowUser(
            name=new_user.name,
            email=new_user.email,
            mobile=new_user.mobile,
            dob=new_user.dob,
            gender=new_user.gender,
            role=new_user.role
        )
    )
