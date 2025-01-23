from fastapi import APIRouter, Depends, status, HTTPException
# Сессия БД
from sqlalchemy.orm import Session
# Функция подключения к БД
from app.backend.db_depends import get_db
# Аннотации, Модели БД и Pydantic
from typing import Annotated
from app.models import User
from app.schemas import CreateUser, UpdateUser
# Функции работы с записями
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify

router2 = APIRouter(prefix='/user', tags=['user'])

@router2.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users

@router2.get('/user_id')
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalars(select(User).where(User.id == user_id)).all()
    if user:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )

@router2.post('/create')
async def create_user(db: Annotated[Session, Depends(get_db)], create_user: CreateUser):
    user = db.scalars(select(User).where(User.username==create_user.username)).all()
    if not user:
        db.execute(insert(User).values(username=create_user.username, firstname=create_user.firstname,
                                   lastname=create_user.lastname, age=create_user.age,
                                   slug=slugify(create_user.username)))
        db.commit()
        return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with that name already exists'
        )

@router2.put('/update')
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int, update_user: UpdateUser):
    user = db.scalars(select(User).where(User.id==user_id)).all()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    db.execute(update(User).where(User.id == user_id).values(
        firstname=update_user.firstname,
        slug=slugify(update_user.firstname),
        lastname=update_user.lastname, age=update_user.age))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User update is successful'
    }

@router2.delete('/delete')
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalars(select(User).where(User.id==user_id)).all()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found'
        )
    else:
        db.execute(delete(User).where(User.id == user_id))
        db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'User delete is successful'
        }

