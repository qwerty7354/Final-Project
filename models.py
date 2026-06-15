from datetime import datetime
from sqlalchemy import ForeignKey
from ext import db, login_manager
from flask_login import UserMixin


class BaseModel:
    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save():
        db.session.commit()


class User(db.Model, BaseModel, UserMixin):
    __tablename__ = "users"

    id       = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    role     = db.Column(db.String(), default="Guest")

    ratings  = db.relationship("Rating",  backref="user", lazy=True)
    comments = db.relationship("Comment", backref="user", lazy=True)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


class Book(db.Model, BaseModel):
    __tablename__ = "books"

    id          = db.Column(db.Integer(), primary_key=True)
    title       = db.Column(db.String(),  nullable=False)
    author      = db.Column(db.String(),  nullable=False)
    year        = db.Column(db.Integer(), nullable=False)
    genre       = db.Column(db.String(),  nullable=False)
    description = db.Column(db.Text(),    default="")
    image       = db.Column(db.String(),  default="default_image.jpg")

    ratings  = db.relationship("Rating",  backref="book", lazy=True)
    comments = db.relationship("Comment", backref="book", lazy=True)


class Rating(db.Model, BaseModel):
    __tablename__ = "ratings"

    id      = db.Column(db.Integer(), primary_key=True)
    score   = db.Column(db.Integer(), nullable=False)
    book_id = db.Column(db.Integer(), ForeignKey("books.id"), nullable=False)
    user_id = db.Column(db.Integer(), ForeignKey("users.id"), nullable=False)


class Comment(db.Model, BaseModel):
    __tablename__ = "comments"

    id         = db.Column(db.Integer(),  primary_key=True)
    text       = db.Column(db.Text(),     nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    book_id    = db.Column(db.Integer(),  ForeignKey("books.id"), nullable=False)
    user_id    = db.Column(db.Integer(),  ForeignKey("users.id"), nullable=False)
