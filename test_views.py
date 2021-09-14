import os
from unittest import TestCase
from sqlalchemy import exc
import json

from models import db, User, Movie, Character, Quote, FavChar, FavQuote, Comment

os.environ['DATABASE_URL'] = "postgresql:///lotr_test"
from app import app, CURR_USER_KEY, get_movies, get_characters, get_quotes

app.config['WTF_CSRF_ENABLED'] = False

class ViewsTestCase(TestCase):
    """Test views(?)"""

    def setUp(self):
        """Test client and sample users"""

        db.session.remove()
        db.drop_all()
        db.create_all()

        client = app.test_client()

        self.client = client

        u1 = User(
            username="user1",
            email="user1@gmail.com",
            password="password"
        )
        db.session.add(u1)

        db.session.commit()

        self.u1 = u1

    def tearDown(self):
        res = super().tearDown()
        # what is this
        return res

    def test_signup(self):
        """/signup a test user"""
        
        with self.client as client:      
            res = client.post("/signup", data={
                "username": "test",
                "email": "test@gmail.com",
                "password": "testing",
                "image_url": "",
                "bio": "test"
            }, follow_redirects=False)
            self.assertEqual(res.status_code, 302)

            user = User.query.get(2)
            self.assertEqual(user.username, "test")

    def test_signup_page(self):
        """login page"""

        with self.client as client:

            res = client.get("/signup")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<button type="submit" class="btn btn-success mx-2">Create User</button>', html)

    # def test_login(self):
    #     """test /login"""
        
    #     with self.client as client:
    #         res = client.post("/login", data={"username": "user1", "password": "password"}, follow_redirects=False)
            
    #         self.assertEqual(res.status_code, 302)

    def test_login_page(self):
        """login page"""

        with self.client as client:

            res = client.get("/login")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<button type="submit" class="btn btn-success mx-2">Login</button>', html)
    

    def test_logout(self):
        """"""
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1.id
        
            res = client.get("/logout")

            self.assertEqual(res.status_code, 302)

    def test_user_page(self):
        """test user page html"""

        with self.client as client:

            res = client.get(f"/users/{self.u1.id}")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f"<h3><b>{self.u1.username}</b></h3>", html)

    # def test_users_edit(self):
    #     """test user edit"""

    #     with self.client as client:
    #         with client.session_transaction() as session:
    #             session[CURR_USER_KEY] = self.u1.id

    #         res = client.post(f"/users/edit", data={
    #             "username": "user1",
    #             "email": "user1@gmail.com",
    #             "password": "password",
    #             "bio": "test"
    #         }, follow_redirects=False)

    #         self.assertEqual(res.status_code, 302)

    #         user = User.query.get(2)
    #         self.assertEqual(user.bio, "test")

    def test_edit_page(self):
        """test user page html"""

        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1.id
            
            res = client.get(f"/users/edit")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<button type="submit" class="btn btn-success mx-2">Edit User</button>', html)
    
    def test_delete(self):
        """test /delete route"""

        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1.id

            res = client.get("/users/delete")

            self.assertEqual(res.status_code, 302)
            self.assertFalse(User.query.all())

    def test_faving_char(self):
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1.id

        testchar = Character(
            id = "test",
            name = "test"
        )
        db.session.add(testchar)
        db.session.commit()

        res = client.post(f"/users/fav_char/{testchar.id}")

        testfav = FavChar.query.one()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(testfav.user_id, 1)
        self.assertEqual(testfav.char_id, "test")
        # how to fix detached instanced error? 

    def test_faving_quote(self):
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1.id

        testquote = Quote(
            id = "test",
            dialog = "test"
        )
        db.session.add(testquote)
        db.session.commit()

        res = client.post(f"/users/fav_quote/{testquote.id}")

        testfav = FavQuote.query.one()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(testfav.user_id, 1)
        self.assertEqual(testfav.quote_id, "test")

    def test_homepage(self):
        with app.test_client() as client:
            
            res = client.get('/')

            self.assertEqual(res.status_code, 200)

    def test_results(self):
        with app.test_client() as client:

            testchar = Character(
                id = "test",
                name = "test"
            )
            db.session.add(testchar)
            db.session.commit()

            res = client.post("/results", data={"search": "test"})
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)          
            self.assertIn('<td scope="col">test</td></col>', html)

    def test_random(self):
        with app.test_client() as client:

            get_movies()
            get_characters()
            get_quotes()

            res = client.get("/random")

            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(json.loads(res.get_data().decode())), 3)

    def test_movies_page(self):
        with app.test_client() as client:
            
            get_movies()

            res = client.get('/movies')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f'<p class="card-text d-flex justify-content-center">The Return of the King</p>', html)

    def test_movie_page(self):
        with app.test_client() as client:

            testmovie = Movie(
                id = "test",
                name = "test"
            )
            db.session.add(testmovie)
            db.session.commit()

            res = client.get(f"/movies/{testmovie.id}")
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn(f'<h3 class="text-white"><b>{testmovie.name}</b></h3>', html)

    def test_characters_page(self):
        with app.test_client() as client:

            testmovie = Movie(
                id = "test1",
                name = "test"
            )
            db.session.add(testmovie)
            testchar = Character(
                id = "test2",
                name = "test"
            )
            db.session.add(testchar)
            db.session.commit()

            res = client.get("characters")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f'<td scope="col">{testchar.name}</td></col>', html)


    def test_character_page(self):
        with app.test_client() as client:

            testchar = Character(
                id = "test",
                name = "test"
            )
            db.session.add(testchar)
            db.session.commit()

            res = client.get(f"/characters/{testchar.id}")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f'<h3 class="text-white"><b>{testchar.name}</b></h3><br>', html)
    
    def test_comment_character(self):
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1.id

            testchar = Character(
                id = "test",
                name = "test"
            )
            db.session.add(testchar)
            db.session.commit()

            res = client.post(f"/characters/{testchar.id}/add-comment", data={"comment": "test"})

            testcomment = Comment.query.one()

            self.assertEqual(res.status_code, 302)
            self.assertEqual(testcomment.comment, "test")
            self.assertEqual(testcomment.user_id, 1)
            self.assertEqual(testcomment.char_id, "test")
            
            
    def test_comment_character_page(self):
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1.id

            testchar = Character(
                id = "test",
                name = "test"
            )
            db.session.add(testchar)
            db.session.commit()

            res = client.get(f"/characters/{testchar.id}/add-comment")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<button type="submit" class="btn btn-success mx-2">Submit Comment</button>', html)

    def test_quotes_page(self):
        with app.test_client() as client:

            testmovie = Movie(
                id = "test1",
                name = "test"
            )
            db.session.add(testmovie)
            testquote = Quote(
                id = "test2",
                dialog = "test"
            )
            db.session.add(testquote)
            db.session.commit()

            res = client.get("/quotes")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f'<button type="button" class="btn btn-success btn-lg btn-block text-white mb-2">Log in to be able to like your favorite quotes!</button>', html)


    def test_character_page(self):
        with app.test_client() as client:

            testquote = Quote(
                id = "test",
                dialog = "test"
            )
            db.session.add(testquote)
            db.session.commit()

            res = client.get(f"/quotes/{testquote.id}")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f'<p>{testquote.dialog}</p>', html)
    
    def test_comment_character(self):
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1.id

            testquote = Quote(
                id = "test",
                dialog = "test"
            )
            db.session.add(testquote)
            db.session.commit()

            res = client.post(f"/quotes/{testquote.id}/add-comment", data={"comment": "test"})

            testcomment = Comment.query.one()

            self.assertEqual(res.status_code, 302)
            self.assertEqual(testcomment.comment, "test")
            self.assertEqual(testcomment.user_id, 1)
            self.assertEqual(testcomment.quote_id, "test")
            
            
    def test_comment_character_page(self):
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1.id

            testquote = Quote(
                id = "test",
                dialog = "test"
            )
            db.session.add(testquote)
            db.session.commit()

            res = client.get(f"/quotes/{testquote.id}/add-comment")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<button type="submit" class="btn btn-success mx-2">Submit Comment</button>', html)

    def test_delete_comment(self):
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.u1.id
        
            testquote = Quote(
                id = "test",
                dialog = "test"
            )
            db.session.add(testquote)
            db.session.commit()
            testcomment = Comment(
                comment = "comment",
                user_id = self.u1.id,
                quote_id = testquote.id
            )
            db.session.add(testcomment)
            db.session.commit()

            res = client.get("/comments/1/delete")

            self.assertEqual(res.status_code, 302)