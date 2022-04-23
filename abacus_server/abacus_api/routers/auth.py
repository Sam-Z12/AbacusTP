from fastapi import APIRouter, HTTPException, Depends, APIRouter, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..schemas import schemas

from .. import database, db_models, utils, oauth2
router = APIRouter(
    tags=['Authentication']
)


@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(db_models.User).filter(
        db_models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    # Pass in what you want in the payload section of the access token
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token,
            "token_type": "bearer"}
