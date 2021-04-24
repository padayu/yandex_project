import datetime
import sqlalchemy
from sqlalchemy import orm

from db_session import SqlAlchemyBase

from sqlalchemy_serializer import SerializerMixin


class Author(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'authors'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    books = sqlalchemy.Column(sqlalchemy.String, nullable=True)