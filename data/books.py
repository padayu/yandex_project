import datetime
import sqlalchemy
from sqlalchemy import orm

from db_session import SqlAlchemyBase

from sqlalchemy_serializer import SerializerMixin


class Book(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    file = sqlalchemy.Column(sqlalchemy.String)
    user_uploaded = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("authors.id"))
    author_name = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("authors.name"))
    user_uploaded_name = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.username"))