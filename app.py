from flask import Flask, render_template, request, jsonify, redirect, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Movie, Character, Quote, Comment
from forms import CreateUserForm, LoginForm, AddCommentForm
import requests
from sqlalchemy.exc import IntegrityError
import random
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

app.config['SECRET_KEY'] = "whatnow"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///lotr'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

url = 'https://the-one-api.dev/v2'
token = os.environ.get("TOKEN")
headers = {'Authorization': f'Bearer {token}'}
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



# user ------------------



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
        prev_url = session['CURR_PATH']
        return redirect(f"{prev_url}")

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
            prev_url = session['CURR_PATH']
            return redirect(f"{prev_url}")

        else:
            flash("Failed to log in", "danger")
            return redirect("/login")
    
    return render_template('users/login.html', form=form)

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
    
    return render_template("users/edit.html", form=form)

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



# api ------------------

@app.route("/get-movies")
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

        db.session.add(_movie)
        db.session.commit()

    prev_url = session['CURR_PATH']
    return redirect(f"{prev_url}")

@app.route("/get-characters-quotes")
def get_quotes():
    """Get quotes, and characters associated, from api. Redirect to previous url."""

    # quotes = {}
    # chars = {}
    i = 0
    ran = list(range(2,500))

    while i < 100:

        mnum = random.randrange(0,2)
        qnum = random.choice(ran)
        movies = ["b", "c", "d"]

        
        res = requests.get("https://the-one-api.dev/v2/movie/5cd95395de30eff6ebccde5" + movies[mnum] + "/quote", headers=headers)
        
        print(res)

        if res == None:
            ran.remove(qnum)
            i+=1
            continue

        res = res.json()

        # if not Quote.query.get(res["docs"][qnum]["_id"]):
        #     quote = {
        #             "id": res["docs"][qnum]["_id"],
        #             "dialog": res["docs"][qnum]["dialog"],
        #             "movie_id": res["docs"][qnum]["movie"],
        #             "char_id": res["docs"][qnum]["character"]
        #     }
        #     quotes[i] = quote

        if not Character.query.get(res["docs"][qnum]["character"]):
            resp = requests.get("https://the-one-api.dev/v2/character/" + res["docs"][qnum]["character"], headers=headers)
            
            if resp == None:
                ran.remove(qnum)
                i+=1                
                continue
            
            resp = resp.json()

            if resp["docs"][0]["name"] == "MINOR_CHARACTER":
                ran.remove(qnum)
                i+=1
                continue

            # char = {
            #         "id": resp["docs"][0]["_id"],
            #         "name": resp["docs"][0]["name"],
            #         "race": resp["docs"][0]["race"],
            #         "gender": resp["docs"][0]["gender"],
            #         "birth": resp["docs"][0]["birth"],
            #         "death": resp["docs"][0]["death"],
            #         "realm": resp["docs"][0]["realm"],
            #         "hair": resp["docs"][0]["hair"],
            #         "height": resp["docs"][0]["height"],
            #         "spouse": resp["docs"][0]["spouse"]
            # }
            # chars[i] = char

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
    
    prev_url = session['CURR_PATH']
    return redirect(f"{prev_url}")



# pages  -------------------------------


@app.route("/")
def homepage():
    """Hompage"""

    movies = Movie.query.all()
    quotes = Quote.query.all()
    chars = Character.query.all()
    
    session['CURR_PATH'] = request.path
    return render_template("homepage.html", movies=movies, quotes=quotes, chars=chars)

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

    quotes = Quote.query.all()
    
    length = list(range(0,len(quotes)))
    results = {}

    for i in range(0,10):

        num = random.choice(length)
        data = {
            "id": quotes[num].id,
            "short_id": quotes[num].id[-4:],
            "dialog": quotes[num].dialog,
            "movie": Movie.query.get(quotes[num].movie_id).name,
            "movie_id": quotes[num].movie_id,
            "char": Character.query.get(quotes[num].char_id).name,
            "char_id": quotes[num].char_id,
            "faveduser": quotes[num].faveduser
        }
        results[i] = data
        length.remove(num)

    return jsonify(quotes=results)



# movies -------------



@app.route("/movies")
def movies_page():
    """Get movies from api, render page"""

    movies = Movie.query.all()    
    fotr = Movie.query.get("5cd95395de30eff6ebccde5c")
    ttt = Movie.query.get("5cd95395de30eff6ebccde5b")
    rotk= Movie.query.get("5cd95395de30eff6ebccde5d")
    
    session['CURR_PATH'] = request.path
    return render_template("movies/movies.html", movies=movies, fotr=fotr, ttt=ttt, rotk=rotk)

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