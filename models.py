from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class FavChar(db.Model):
    """User favorited"""

    __tablename__='favchars'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    char_id = db.Column(db.Text, db.ForeignKey('characters.id', ondelete='cascade'), primary_key=True)

class FavQuote(db.Model):

    __tablename__='favquotes'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    quote_id = db.Column(db.Text, db.ForeignKey('quotes.id', ondelete='cascade'), primary_key=True)

class Comment(db.Model):
    """User comments on characters"""

    __tablename__="comments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    char_id = db.Column(db.Text, db.ForeignKey('characters.id', ondelete='cascade'))
    quote_id = db.Column(db.Text, db.ForeignKey('quotes.id', ondelete='cascade'))

# class QuoteComment(db.Model):
#     """User comments on quotes"""

#     __tablename__="quotecomms"

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     comment = db.Column(db.Text, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
#     quote_id = db.Column(db.Text, db.ForeignKey('quotes.id', ondelete='cascade'))


class User(db.Model):
    """Users table"""

    __tablename__="users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, default="http://www.spore.com/static/image/500/338/000/500338000894_lrg.png")
    bio = db.Column(db.Text)

    favquotes = db.relationship("Quote", 
                                secondary="favquotes", 
                                primaryjoin=(FavQuote.user_id == id),
                                backref='faveduser',
                                passive_deletes=True)
    
    favchars = db.relationship("Character", 
                                secondary="favchars", 
                                primaryjoin=(FavChar.user_id == id),
                                backref='faveduser', 
                                passive_deletes=True)

    comms = db.relationship("Comment", passive_deletes=True, backref="user")

    # quotecomments = db.relationship("QuoteComment", passive_deletes=True, backref="user")

    commedchars = db.relationship("Character", 
                                secondary="comments", 
                                primaryjoin=(Comment.user_id == id),
                                passive_deletes=True)

    commedquotes = db.relationship("Quote", 
                                secondary="comments", 
                                primaryjoin=(Comment.user_id == id), 
                                passive_deletes=True)                                

    @classmethod
    def signup(cls, username, email, password, image_url, bio):
        """Sign up user"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            bio=bio
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Movie(db.Model):
    """Movies"""

    __tablename__="movies"

    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    runtime = db.Column(db.Integer)
    budget = db.Column(db.Integer)
    revenue = db.Column(db.Integer)
    academynoms = db.Column(db.Integer)
    academywins = db.Column(db.Integer)
    rotten_t_score = db.Column(db.Integer)
    image_url = db.Column(db.Text)

    quotes = db.relationship("Quote", passive_deletes=True, backref="movie")



class Character(db.Model):
    """Characters"""

    __tablename__='characters'

    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    race = db.Column(db.Text)
    birth = db.Column(db.Text)
    death = db.Column(db.Text)
    realm = db.Column(db.Text)
    hair = db.Column(db.Text)
    height = db.Column(db.Text)
    spouse = db.Column(db.Text)
    gender= db.Column(db.Text)

    quotes = db.relationship("Quote", passive_deletes=True, backref="char")

    comms = db.relationship("Comment", passive_deletes=True, backref="char")

    commedusers = db.relationship("User", 
                        secondary="comments", 
                        primaryjoin=(Comment.char_id == id))


class Quote(db.Model):
    """Quotes from movies only"""

    __tablename__="quotes"

    id = db.Column(db.Text, primary_key=True)
    dialog = db.Column(db.Text, nullable=False)
    movie_id = db.Column(db.Text, db.ForeignKey('movies.id', ondelete='cascade'))
    char_id = db.Column(db.Text, db.ForeignKey('characters.id', ondelete='cascade'))

    comms = db.relationship("Comment", passive_deletes=True, backref="quote")
    
    commedusers = db.relationship("User", 
                            secondary="comments", 
                            primaryjoin=(Comment.quote_id == id))