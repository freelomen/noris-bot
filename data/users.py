import sqlalchemy
from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    fio = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    birthday = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    phone = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sex = sqlalchemy.Column(sqlalchemy.String, nullable=True)
