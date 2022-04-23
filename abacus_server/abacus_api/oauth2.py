from base64 import encode
from jose import JWTError, jwt
from datetime import datetime, time, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm.session import Session

from .schemas import schemas


from .utils import verify
from . import database, db_models
from ..config import settings
# Just mashed keyboard to make secret key
SECRET_KEY = f"{settings['ABACUS_SECRET_KEY']}"
ALGORITHM = f"{settings['ABACUS_ALGORITHM']}"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    settings['ABACUS_ACCESS_TOKEN_EXPIRE_MINUTES'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=id)

    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    print("Getting current user")
    credentials_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                          detail=f"Could not validate credetials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception)
    user = db.query(db_models.User).filter(
        db_models.User.id == token.id).first()
    return user
