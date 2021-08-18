# pass: kankersore
# token: MZ8oiSJNOwk0KtJdUItp

from flask import Flask, render_template, request, jsonify, redirect, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Movie, Character, Quote, FavChar, FavQuote
from forms import CreateUserForm, LoginForm
import requests
from sqlalchemy.exc import IntegrityError
import random



app = Flask(__name__)

app.config['SECRET_KEY'] = "whatnow"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///lotr'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

url = 'https://the-one-api.dev/v2'
headers = {'Authorization': 'Bearer MZ8oiSJNOwk0KtJdUItp'}
CURR_USER_KEY = "curr_user"
CURR_PATH = "curr_path"

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user"""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]



# user stuff ------------------



@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle creating user"""

    form = CreateUserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                image_url=form.image_url.data or User.image_url.default.arg,
                bio=form.bio.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username taken", "danger")
            return render_template('users/create.html', form=form)

        do_login(user)
        return redirect("/")

    else:
        return render_template('users/create.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """handling user login"""

    form = LoginForm()

    if form.validate_on_submit():
        user= User.authenticate(
            username=form.username.data,
            password=form.password.data
        )

        if user:
            do_login(user)
            flash("Successfully logged in", "success")
            return redirect("/")
        else:
            flash("Failed to log in", "danger")
            return redirect("/login")
    
    return render_template('users/login.html', form=form)

@app.route("/logout")
def logout():
    """logout handler"""

    do_logout()
    flash("Succussfully logged out", "success")
    return redirect('/login')

@app.route("/users/<int:user_id>")
def user_page(user_id):
    """user page"""

    if not g.user:
        flash("Access denied", "danger")
        return redirect("/login")

    user = User.query.get_or_404(user_id)


    return render_template("users/page.html", user=user)

@app.route("/users/edit", methods=["GET", "POST"])
def edit_user():

    if not g.user:
        flash("What are you doing here", "danger")
        return redirect('/login')

    form = CreateUserForm(obj=g.user)

    if form.validate_on_submit():
        user = User.authenticate(g.user.username, form.password.data)

        if user:
            g.user.username = form.username.data
            g.user.email = form.email.data
            g.user.image_url = form.image_url.data or User.image_url.default.arg
            g.user.bio = form.bio.data
            db.session.commit()

            return redirect(f"{g.user.id}")
    
        flash("NICE TRY", "danger")
        return redirect("/")
    
    return render_template("users/edit.html", form=form)

@app.route("/users/delete")
def delete_user():

    if not g.user:
        flash("Access denied", "danger")
        return redirect("/login")

    do_logout()
    db.session.delete(g.user)
    db.session.commit()

    flash("Deleted user", "success")
    return redirect("/signup")

@app.route("/users/fav_char/<char_id>", methods=["POST"])
def char_fav(char_id):

    if not g.user:
        flash("Log in to favorite characters", "danger")
        return redirect("/")

    char = Character.query.get_or_404(char_id)

    if char in g.user.favchars:
        g.user.favchars.remove(char)
        db.session.commit()
    else:
        g.user.favchars.append(char)
        db.session.commit()
    
    return redirect("/characters")

@app.route("/users/fav_quote/<quote_id>", methods=["POST"])
def quote_fav(quote_id):

    if not g.user:
        flash("Log in to favorite quotes", "danger")
        return redirect("/")

    quote = Quote.query.get_or_404(quote_id)

    if quote in g.user.favquotes:
        g.user.favquotes.remove(quote)
        db.session.commit()
    else:
        g.user.favquotes.append(quote)
        db.session.commit()
    
    return redirect("/quotes")


# api stuff ------------------

# how do i call this stuff without a button

@app.route("/get-movies")
def get_movies():
    """get movies from api"""
    
    if not g.user:
        flash("Please log in", "danger")
        return redirect("/login")

    res = requests.get("https://the-one-api.dev/v2/movie", headers=headers)
    res = res.json()

    for dict in res["docs"]:

        _movie = Movie(
            id = dict["_id"],
            name = dict["name"],
            runtime = dict["runtimeInMinutes"],
            budget = dict["budgetInMillions"],
            revenue = dict["boxOfficeRevenueInMillions"],
            academynoms = dict["academyAwardNominations"],
            academywins = dict["academyAwardWins"],
            rotten_t_score = dict["rottenTomatoesScore"]
        )

        if _movie.id == "5cd95395de30eff6ebccde5c":
            _movie.image_url = "https://m.media-amazon.com/images/I/81EBp0vOZZL._AC_SY741_.jpg"
        if _movie.id == "5cd95395de30eff6ebccde5b":
            _movie.image_url = "https://m.media-amazon.com/images/I/81eqQvveI6L._AC_SY679_.jpg"
        if _movie.id == "5cd95395de30eff6ebccde5d":
            _movie.image_url = "https://m.media-amazon.com/images/I/91UP+jG-ypL._AC_SY679_.jpg"

        db.session.add(_movie)
        db.session.commit()

    return redirect("/movies")

@app.route("/get-characters-quotes")
def get_quotes():
    """Get quotes, and characters associated, from api"""

    if not g.user:
        flash("Please log in", "danger")
        return redirect("/login")

    quotes = {}
    chars = {}
    i = 0
    ran = list(range(2,500))

    while i < 20:

        mnum = random.randrange(0,2)
        qnum = random.choice(ran)
        movies = ["b", "c", "d"]

        
        res = requests.get("https://the-one-api.dev/v2/movie/5cd95395de30eff6ebccde5" + movies[mnum] + "/quote", headers=headers)
        # api doesn't provide a way to get random quotes, but this jank method only works with the original trilogy. who cares about the hobbit movies anyway right? haha..
        # is there a method? my insomnia get requests capped out at 1000 while there were like 2600. Problem is they were ordered by movie so the first 100 would have all been from one movie.
        
        res = res.json()

        if not Quote.query.get(res["docs"][qnum]["_id"]):
            quote = {
                    "id": res["docs"][qnum]["_id"],
                    "dialog": res["docs"][qnum]["dialog"],
                    "movie_id": res["docs"][qnum]["movie"],
                    "char_id": res["docs"][qnum]["character"]
            }
            quotes[i] = quote

        if not Character.query.get(res["docs"][qnum]["character"]):
            resp = requests.get("https://the-one-api.dev/v2/character/" + res["docs"][qnum]["character"], headers=headers)
            resp = resp.json()


            char = {
                    "id": resp["docs"][0]["_id"],
                    "name": resp["docs"][0]["name"],
                    "race": resp["docs"][0]["race"],
                    "gender": resp["docs"][0]["gender"],
                    "birth": resp["docs"][0]["birth"],
                    "death": resp["docs"][0]["death"],
                    "realm": resp["docs"][0]["realm"],
                    "hair": resp["docs"][0]["hair"],
                    "height": resp["docs"][0]["height"],
                    "spouse": resp["docs"][0]["spouse"]
            }
            chars[i] = char

            _char = Character(
                id = resp["docs"][0]["_id"],
                name = resp["docs"][0]["name"],
                race = resp["docs"][0]["race"],
                gender = resp["docs"][0]["gender"],
                birth = resp["docs"][0]["birth"],
                death = resp["docs"][0]["death"],
                realm = resp["docs"][0]["realm"],
                hair = resp["docs"][0]["hair"],
                height = resp["docs"][0]["height"],
                spouse = resp["docs"][0]["spouse"]
            )
            db.session.add(_char)             

        if not Quote.query.get(res["docs"][qnum]["_id"]):
            _quote = Quote(
                id = res["docs"][qnum]["_id"],
                dialog = res["docs"][qnum]["dialog"],
                movie_id = res["docs"][qnum]["movie"],
                char_id = res["docs"][qnum]["character"]
            )
            db.session.add(_quote)
            db.session.commit()

        ran.remove(qnum)
        i+=1
    
    return redirect("/characters")



# page stuff ----------------------


@app.route("/")
def homepage():
    """Hompage"""

    if not g.user:
        flash("Please log in", "warning")
        return redirect("/login")

    movies = Movie.query.all()
    quotes = Quote.query.all()
    chars = Character.query.all()
 
    return render_template("pages/homepage.html", movies=movies, quotes=quotes, chars=chars)

@app.route("/movies")
def movies_page():
    """Get movies from api, render page"""

    if not g.user:
        flash("Please log in", "danger")
        return redirect("/login")

    movies = Movie.query.all()    
    fotr = Movie.query.get_or_404("5cd95395de30eff6ebccde5c")
    ttt = Movie.query.get_or_404("5cd95395de30eff6ebccde5b")
    rotk= Movie.query.get_or_404("5cd95395de30eff6ebccde5d")

    return render_template("pages/movies.html", movies=movies, fotr=fotr, ttt=ttt, rotk=rotk)

@app.route("/movies/<movie_id>")
def movie_page(movie_id):
    """Single movie page with quotes maybe? maybe some main characters? def info"""

    if not g.user:
        flash("Please log in", "danger")
        return redirect("/login")

    movie = Movie.query.get_or_404(movie_id)

    return render_template("pages/movie_page.html", movie=movie)


@app.route("/characters")
def chars_page():
    """characters page from existing quotes?"""

    if not g.user:
        flash("Please log in", "danger")
        return redirect("/login")

    movies = Movie.query.all()
    chars = Character.query.all()


    return render_template("pages/characters.html", chars=chars, movies=movies)

@app.route("/characters/<char_id>")
def char_page(char_id):

    if not g.user:
        flash("Please log in", "danger")
        return redirect("/login")

    char = Character.query.get_or_404(char_id)

    if not char:
        flash("Character is not in database", "danger")
        return redirect("/login")

    return render_template("pages/character_page.html", char=char)

@app.route("/quotes")
def quotes_page():
    """Quotes page"""

    if not g.user:
        flash("Please log in", "danger")
        return redirect("/login")

    movies = Movie.query.all()
    quotes = Quote.query.all()

    return render_template("pages/quotes.html", quotes=quotes, movies=movies)


    # i'd really love it if i knew how to save the past path/url and redirect back to it