from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Movie, Character, Quote, Comment, FavQuote, FavChar

from app import app
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///lotr_test'

class ViewsTestCase(TestCase):
    """Test user model"""

    def setUp(self):
        """Test client and sample users"""

        db.session.remove()
        db.drop_all()
        db.create_all()

        u1 = User(
            username="user1",
            email="user1@gmail.com",
            password="password"
        )
        db.session.add(u1)
        
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


        self.u1 = u1
        self.movie1 = movie1
        self.char1 = char1
        self.quote1 = quote1

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        # what is this
        return res