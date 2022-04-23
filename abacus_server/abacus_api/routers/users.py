
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

from ..schemas import schemas

from ..database import get_db
from .. import db_models, utils
from ...config import settings


router = APIRouter(
    prefix="/users",
    tags=['Users']
)


@router.post("/", status_code=HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hash password
    hashed_password = utils.hash(user.password)

    # Verfies that I am the only one who can create a user
    if not utils.verify(str(settings['ABACUS_PASSWORD']), hashed_password):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    user.password = hashed_password

    new_user = db_models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(db_models.User).filter(db_models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} does not exist")

    return user
