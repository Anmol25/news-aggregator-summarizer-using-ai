import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from database.session import get_db
from database.models import Users
from database.operations import create_user_in_db, get_user_history, check_user_in_db
from sqlalchemy.orm import Session
from users.schemas import Token, User, UserCreate
from users.services import authenticate_user, create_access_token, get_current_active_user, get_password_hash

logger = logging.getLogger(__name__)

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()


@router.post("/create_user")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new User"""
    try:
        # Check if user exist in DB
        exist_user = check_user_in_db(user, db)
        if exist_user:
            raise HTTPException(status_code=409, detail=exist_user)
        # Hash Password
        user.password = get_password_hash(user.password)
        # Create User in DB
        user_created = create_user_in_db(user, db)
        if not user_created:
            raise HTTPException(
                status_code=500, detail="Failed to create User")
        return {"response": "User Successfully created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),  db: Session = Depends(get_db)):
    """Create a new Access Token"""
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: Users = Depends(get_current_active_user)):
    """Returns current user details"""
    try:
        current_user = User.model_validate(current_user)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not logged in.")
        return current_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/userhistory")
async def get_current_user_history(current_user: Users = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Returns the History of current history."""
    try:
        if current_user:
            history = get_user_history(current_user.id, db)
            return history
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not logged in.")
    except Exception as e:
        logger.error(f"Error in retrieving current user history: {e}")
