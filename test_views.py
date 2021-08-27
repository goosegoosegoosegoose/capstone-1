from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Movie, Character, Quote, Comment, FavQuote, FavChar

from app import app
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///lotr_test'

db.create_all()

class ViewsTestCase(TestCase):
        """Test user model"""

        def setUp(self):
            """Test client and sample users"""

            db.drop_all()
            db.create_all()

            u1 = User.signup("user1", "email1@gmail.com", "pw")
            u1.id = 11

            movie1 = Movie(
                id = "m1",
                name = "Dingo's Adventure"
            )
            db.session.add(movie1)

            char1 = Character(
                id = "c1",
                name = "Dingo"
            )
            db.session.add(char1)

            quote1 = Quote(
                id = "q1",
                dialog = "Yeehaw",
                movie_id = "m1",
                char_id = "c1"
            )
            db.session.add(quote1)

            db.session.commit()

            u1 = User.query.get(11)
            movie1 = Movie.query.get("m1")
            char1 = Character.query.get("c1")
            quote1 = Quote.query.get("q1")


            self.u1 = u1
            self.movie1 = movie1
            self.char1 = char1
            self.quote1 = quote1

            self.client = app.test_client()