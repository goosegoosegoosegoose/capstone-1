from flask import Flask, render_template, request, jsonify, redirect, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Movie, Character, Quote, Comment
from forms import CreateUserForm, LoginForm, AddCommentForm
import requests
from sqlalchemy.exc import IntegrityError
import random
import os
from dotenv import load_dotenv
import secrets

app = Flask(__name__)
load_dotenv()

app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///lotr'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

url = 'https://the-one-api.dev/v2'
token = os.environ.get("TOKEN")
headers = {'Authorization': f'Bearer {token}'}
CURR_USER_KEY = "curr_user"
CURR_PATH = "curr_path"

connect_db(app)

# Pre-load functions
def get_movies():
    """get movies from api"""

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
        if _movie.id == "5cd95395de30eff6ebccde58":
            _movie.image_url = "https://m.media-amazon.com/images/I/71mOQV8-GzL._AC_SL1007_.jpg"
        if _movie.id == "5cd95395de30eff6ebccde59":
            _movie.image_url = "https://m.media-amazon.com/images/I/7145Wo9GjlL._AC_SL1006_.jpg"
        if _movie.id == "5cd95395de30eff6ebccde5a":
            _movie.image_url = "https://m.media-amazon.com/images/I/A1QbAD2iMVL._AC_SL1500_.jpg"

        db.session.add(_movie)

    db.session.commit()

def get_characters():
    """Get all characters except MINOR_CHARACTER name ones from api"""

    res = requests.get("https://the-one-api.dev/v2/character", headers=headers)
    res = res.json()

    for char in res["docs"]:

        if char["name"] == "MINOR_CHARACTER":
            continue
        
        _char = Character(
            id = char["_id"],
            name = char["name"],
            race = char["race"],
            gender = char.get("gender", ""),
            birth = char["birth"],
            death = char["death"],
            realm = char["realm"],
            hair = char["hair"],
            height = char["height"],
            spouse = char["spouse"]
        )
        db.session.add(_char)
    
    db.session.commit()

def get_quotes():
    """Get all quotes from api."""

    pages = [1,2,3]

    for page in pages:
        res = requests.get("https://the-one-api.dev/v2/quote?page=" + str(page), headers=headers)
        res = res.json()         


        for quote in res["docs"]:

            if not Character.query.get(quote["character"]):
                continue

            if db.session.query(Quote).filter_by(dialog=quote["dialog"]).first():
                rep = db.session.query(Quote).filter_by(dialog=quote["dialog"]).first()
                if rep.dialog == quote["dialog"] and rep.char_id == quote["character"]:
                    continue
            
            _quote = Quote(
                id = quote["_id"],
                dialog = quote["dialog"],
                movie_id =quote["movie"],
                char_id = quote["character"]
            )
            db.session.add(_quote)
    
    db.session.commit()
    
# pre-load check
if not Movie.query.all():
    get_movies()

if not Character.query.all():
    get_characters()

if not Quote.query.all():
    get_quotes()


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

# user ------------------



@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle creating user"""

    form = CreateUserForm()
    prev_url = session['CURR_PATH']

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
        return redirect(f"{prev_url}")

    else:
        return render_template('users/create.html', form=form, prev_url=prev_url)

@app.route("/login", methods=["GET", "POST"])
def login():
    """handling user login"""

    form = LoginForm()
    prev_url = session['CURR_PATH']

    if form.validate_on_submit():
        user= User.authenticate(
            username=form.username.data,
            password=form.password.data
        )

        if user:
            do_login(user)
            flash("Successfully logged in", "success")
            return redirect(f"{prev_url}")

        else:
            flash("Failed to log in", "danger")
            return redirect("/login")
    
    return render_template('users/login.html', form=form, prev_url=prev_url)

@app.route("/logout")
def logout():
    """logout handler"""

    prev_url = session['CURR_PATH']
    
    if not g.user:
        flash("User is not logged in", "danger")
        return redirect(f'{prev_url}')

    do_logout()
    flash("Succussfully logged out", "success")
    prev_url = session['CURR_PATH']
    return redirect(f"{prev_url}")

@app.route("/users/<int:user_id>")
def user_page(user_id):
    """user page"""

    user = User.query.get_or_404(user_id)
    
    session['CURR_PATH'] = request.path
    return render_template("users/page.html", user=user)

@app.route("/users/edit", methods=["GET", "POST"])
def edit_user():

    prev_url = session['CURR_PATH']
    
    if not g.user:
        flash("Please log in to edit profile", "danger")
        return redirect(f'{prev_url}')

    form = CreateUserForm(obj=g.user)

    if form.validate_on_submit():
        user = User.authenticate(g.user.username, form.password.data)

        if user:
            g.user.username = form.username.data
            g.user.email = form.email.data
            g.user.image_url = form.image_url.data or User.image_url.default.arg
            g.user.bio = form.bio.data
            db.session.commit()

            flash("Succesfully edited profile!", "success")
            return redirect(f"{g.user.id}")
    
        flash("Incorrect password", "danger")
        return redirect(f"/users/edit")
    
    return render_template("users/edit.html", form=form, prev_url=prev_url)

@app.route("/users/delete")
def delete_user():

    prev_url = session['CURR_PATH']
    if not g.user:
        flash("Action unavailable", "danger")
        return redirect(f"{prev_url}")

    do_logout()
    db.session.delete(g.user)
    db.session.commit()

    flash("Deleted user", "success")
    return redirect(f"{prev_url}")


# favoriting --------------


@app.route("/users/fav_char/<char_id>", methods=["POST"])
def char_fav(char_id):

    prev_url = session['CURR_PATH']
    if not g.user:
        flash("Log in to favorite characters", "danger")
        return redirect(f"{prev_url}")

    char = Character.query.get_or_404(char_id)
    action = {}

    if char in g.user.favchars:
        g.user.favchars.remove(char)
        db.session.commit()

        action[1] = 'unlike'
        return jsonify(action=action)

    else:
        g.user.favchars.append(char)
        db.session.commit()

        action[1] = 'like'
        return jsonify(action=action)

@app.route("/users/fav_quote/<quote_id>", methods=["POST"])
def quote_fav(quote_id):

    prev_url = session['CURR_PATH']
    if not g.user:
        flash("Log in to favorite quotes", "danger")
        return redirect(f"{prev_url}")

    quote = Quote.query.get_or_404(quote_id)
    action = {}

    if quote in g.user.favquotes:
        g.user.favquotes.remove(quote)
        db.session.commit()

        action[1] = 'unlike'
        return jsonify(action=action)

    else:
        g.user.favquotes.append(quote)
        db.session.commit()

        action[1] = 'like'
        return jsonify(action=action)




# pages  -------------------------------




@app.route("/")
def homepage():
    """Hompage"""

    movies = Movie.query.all()
    quotes = Quote.query.all()
    chars = Character.query.all()
    r = list(range(0,len(quotes)))
    
    session['CURR_PATH'] = request.path
    return render_template("homepage.html", movies=movies, quotes=quotes, chars=chars, r=r)

@app.route("/results", methods=["POST"])
def search_results():
    """Search form?"""

    query = request.form.get('search')
    print(query)
    search = f"%{query}%"
    chars = Character.query.filter(Character.name.ilike(search)).all()
    quotes = Quote.query.filter(Quote.dialog.ilike(search)).all()

    return render_template("results.html", chars=chars, quotes=quotes, query=query)

@app.route("/random")
def homepage_random_quotes():
    """Get 10 random quotes for webpage"""

    if not g.user:
        status = "unsigned"
        user_id = ""
    else:
        status = "signed"
        user_id = g.user.id

    quotes = Quote.query.all()
    
    length = list(range(0,len(quotes)))
    results = {}

    for i in range(0,20):

        num = random.choice(length)
        faved_user_ids = []

        for user in quotes[num].faveduser:
            faved_user_ids.append(user.id)

        data = {
            "id": quotes[num].id,
            "short_id": quotes[num].id[-4:],
            "dialog": quotes[num].dialog,
            "movie": Movie.query.get(quotes[num].movie_id).name,
            "movie_id": quotes[num].movie_id,
            "char": Character.query.get(quotes[num].char_id).name,
            "char_id": quotes[num].char_id,
            "faveduser": faved_user_ids
        }
        results[i] = data
        length.remove(num)

    return jsonify(quotes=results, status=status, user_id=user_id)




# movies -------------





@app.route("/movies")
def movies_page():
    """Get movies from api, render page"""

    movies = Movie.query.all()    
    
    session['CURR_PATH'] = request.path
    return render_template("movies/movies.html", movies=movies)

@app.route("/movies/<movie_id>")
def movie_page(movie_id):
    """Single movie page with quotes maybe? maybe some main characters? def info"""

    movie = Movie.query.get_or_404(movie_id)
    
    session['CURR_PATH'] = request.path
    return render_template("movies/movie_page.html", movie=movie)




# characters -------------------------------------




@app.route("/characters")
def chars_page():
    """characters page from existing quotes?"""

    movies = Movie.query.all()
    chars = Character.query.all()
    
    session['CURR_PATH'] = request.path
    return render_template("characters/characters.html", chars=chars, movies=movies)

@app.route("/characters/<char_id>")
def char_page(char_id):
    """Character page with affliated quotes and user comments"""

    char = Character.query.get(char_id)
    prev_url = session['CURR_PATH']

    if not char:
        flash("Character is not in database", "danger")
        return redirect(f"{prev_url}")
    
    session['CURR_PATH'] = request.path
    return render_template("characters/character_page.html", char=char)

@app.route("/characters/<char_id>/add-comment", methods=["GET", "POST"])
def add_char_comment(char_id):
    """Add a comment to character"""

    prev_url = session['CURR_PATH']
    if not g.user:
        flash("Log in to comment", "danger")
        return redirect(f"{prev_url}")

    form = AddCommentForm()
    char = Character.query.get_or_404(char_id)

    if form.validate_on_submit():
        comment = Comment(
            comment=form.comment.data,
            user_id=g.user.id,
            char_id=char.id
        )
        db.session.add(comment)
        db.session.commit()

        flash("Comment added!", "success")
        return redirect(f'{prev_url}')
    
    return render_template("characters/char_comment_form.html", form=form, char=char)




# quotes -----------------------





@app.route("/quotes")
def quotes_page():
    """Quotes page"""

    movies = Movie.query.all()
    quotes = Quote.query.all()
    
    session['CURR_PATH'] = request.path
    return render_template("quotes/quotes.html", quotes=quotes, movies=movies)

@app.route("/quotes/<quote_id>")
def quote_page(quote_id):
    """Quote page with user comments"""

    quote = Quote.query.get_or_404(quote_id)
    
    session['CURR_PATH'] = request.path
    return render_template("quotes/quote_page.html", quote=quote)

@app.route("/quotes/<quote_id>/add-comment", methods=["GET", "POST"])
def add_quote_comment(quote_id):
    """Add comment to quote"""

    prev_url = session['CURR_PATH']

    if not g.user:
        flash("Log in to comment", "danger")
        return redirect(f"{prev_url}")

    form = AddCommentForm()
    quote = Quote.query.get_or_404(quote_id)
    prev_url = session['CURR_PATH']

    if form.validate_on_submit():
        comment = Comment(
            comment=form.comment.data,
            user_id=g.user.id,
            quote_id=quote.id
        )
        db.session.add(comment)
        db.session.commit()

        flash("Comment added!", "success")
        return redirect(f'{prev_url}')
    
    return render_template("quotes/quote_comment_form.html", form=form, quote=quote, prev_url=prev_url)

@app.route("/comments/<int:comment_id>/delete")
def delete_comment(comment_id):
    """Delete comment if owner of comment"""

    prev_url = session['CURR_PATH']

    if not g.user:
        flash("Access Denied", "danger")
        return redirect(f"{prev_url}")    

    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()

    flash("Comment deleted!", "success")
    return redirect(f"{prev_url}")