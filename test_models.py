import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Movie, Character, Quote

os.environ['DATABASE_URL'] = "postgresql:///lotr_test"
from app import app


class ModelsTestCase(TestCase):
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


    def test_user_model(self):

        u = User(
            username="user",
            email="email@gmail.com",
            password="hashed"
        )
        db.session.add(u)
        db.session.commit()

        """should be fresh user"""
        self.assertEqual(len(u.favchars), 0)
        self.assertEqual(len(u.favquotes), 0)
        self.assertEqual(len(u.comms), 0)

    def test_user_favoriting_char(self):
        self.u1.favchars.append(self.char1)
        db.session.commit()

        self.assertEqual(len(self.u1.favchars), 1)
        self.assertEqual(len(self.char1.faveduser), 1)

        self.assertEqual(self.u1.favchars[0].id, self.char1.id)
        self.assertEqual(self.char1.faveduser[0].id, self.u1.id)

    def test_user_favoriting_quote(self):
        self.u1.favquotes.append(self.quote1)
        db.session.commit()

        self.assertEqual(len(self.u1.favquotes), 1)
        self.assertEqual(len(self.quote1.faveduser), 1)

        self.assertEqual(self.u1.favquotes[0].id, self.quote1.id)
        self.assertEqual(self.quote1.faveduser[0].id, self.u1.id)

    def test_user_signup(self):

        u2 = User.signup("test", "test@gmail.com", "password", None, "test")
        uid = 2222
        u2.id = uid
        db.session.commit()

        user = User.query.get(uid)
        self.assertEqual(len(db.session.query(User.id).all()), 2)
        self.assertEqual(user.username, "test")
        self.assertEqual(user.email, "test@gmail.com")
        self.assertNotEqual(user.password, "password")
        self.assertNotEqual(user.image_url, None)
        self.assertEqual(user.bio, "test")
        self.assertTrue(user.password.startswith("$2b$"))
        # remember bcrypt

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test@test.com", "password", None, None)
        uid = 123456
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password", None, None)
        uid = 3425
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None, None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None, None)

    def test_movies_model(self):
        id = "m2"
        name = "Dango's Journey"

        movie2 = Movie(
            id = id,
            name = name
        )
        db.session.add(movie2)
        db.session.commit()

        movie2 = Movie.query.get(movie2.id)

        self.assertEqual(movie2.id, id)
        self.assertEqual(movie2.name, name)
        self.assertEqual(len(movie2.quotes), 0)
        self.assertEqual(len(db.session.query(Movie.id).all()), 2)
    
    def test_movie_quotes(self):
        self.movie1.quotes.append(self.quote1)
        db.session.commit()

        self.assertEqual(len(self.movie1.quotes), 1)

        self.assertEqual(self.movie1.quotes[0].id, self.quote1.id) 

    def test_characters_model(self):

        id = "c2"
        name = "Dango"

        char2 = Character(
            id = id,
            name = name
        )
        db.session.add(char2)
        db.session.commit()

        self.assertEqual(char2.id, id)
        self.assertEqual(char2.name, name)
        self.assertEqual(len(char2.quotes), 0)   
        self.assertEqual(len(char2.comms), 0)
        self.assertEqual(len(db.session.query(Character.id).all()), 2)

    def test_quotes_model(self):
        id = "q2"
        dialog = "Nope"
        movie_id = "m1"
        char_id = "c1"

        quote2 = Quote(
            id = id,
            dialog = dialog,
            movie_id = movie_id,
            char_id = char_id
        )
        db.session.add(quote2)
        db.session.commit()

        self.assertEqual(quote2.id, id)
        self.assertEqual(quote2.dialog, dialog)
        self.assertEqual(quote2.movie_id, movie_id)
        self.assertEqual(quote2.char_id, char_id)
        self.assertEqual(len(quote2.comms), 0)
        self.assertEqual(quote2.movie, self.movie1)
        self.assertEqual(quote2.char, self.char1)
        self.assertEqual(len(db.session.query(Quote.id).all()), 2)

# SELECT pg_terminate_backend(pid) from pg_stat_activity WHERE pid <> pg_backend_pid() AND datname = 'lotr_test';