"""Movie Ratings."""

from jinja2 import StrictUndefined
import json
import requests

# from flask.ext.sqlalchemy import SQLAlchemy
# from sqlalchemy import exc

from flask import Flask, render_template, request, redirect, session, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import func

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    top_five = db.session.query(func.count(Rating.score))

    return render_template('homepage.html')

@app.route('/users')
def get_users():
    """Get list of users"""

    users = User.query.all()

    return render_template('user_list.html', users=users)

@app.route('/user-signup')
def user_signup():
    """Render user signup form"""

    return render_template('user-signup.html')

@app.route('/check-user', methods=['POST'])
def check_for_user():
    """Check to see if user exists in db"""

    username = request.form.get('username')
    email = request.form.get('email')

    try:
        User.query.filter(User.email==email).one()
        return jsonify({'code': 0})
    except:
        return jsonify({'code': 1})

@app.route('/add-user', methods=['POST'])
def add_user():
    """Add user"""

    name = request.form.get('name')
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')
    email = request.form.get('email')
    password = request.form.get('password')

    user = User(age=age, zipcode=zipcode, email=email, password=password)

    db.session.add(user)
    db.session.commit()

    flash('Account created')

    return redirect('/')

@app.route('/login', methods=['POST'])
def login():

    email = request.form.get('email')
    password = request.form.get('password')

    try:
        user = User.query.filter(User.email==email).one()
        session['user'] = user.user_id
        flash('Logged in')
        return jsonify({'code': 1})
    except:
        return jsonify({'code': 0})

@app.route('/logout')
def logout():

    print 'at least I got here'

    del session['user']

    flash('Successfully logged out')

    return redirect('/')

@app.route('/users/<user_id>')
def display_user(user_id):


    user = User.query.get(user_id)
    print user

    return render_template('user_info.html', user=user)

@app.route('/movies')
def display_movies():

    movies = Movie.query.order_by(Movie.title).all()

    return render_template('movie_list.html', movies=movies)

@app.route('/movies/<movie_id>')
def display_movie_info(movie_id):


    movie = Movie.query.get(movie_id)

    avg_rating = db.session.query(func.avg(Rating.score)).filter(Rating.movie_id==int(movie_id)).one()

    if 'user' in session:
        user = User.query.get(session['user'])
        rated = Rating.query.filter(Rating.user_id == user.user_id, 
                    Rating.movie_id==movie.movie_id).first()

    else:
        rated = None

    return render_template('movie_details.html', movie=movie, rated=rated, avg_rating=avg_rating[0])


@app.route('/add-rating', methods=['POST'])
def add_rating():

    user = User.query.get(session['user'])
    movie = Movie.query.get(int(request.form.get('movie')))
    score = request.form.get('score')

    try:
        rating = Rating.query.filter(Rating.user_id==user.user_id, Rating.movie_id==movie.movie_id).one()
        
        rating.score = score
        db.session.commit()
        return jsonify({'msg': 'this person has updated the movie rating', 'reload': 1})
    except:
        rating = Rating(user_id=user.user_id, movie_id=movie.movie_id, score=int(score))
        db.session.add(rating)
        db.session.commit()
        return jsonify({'msg': 'this person has not rated this movie but now has', 'reload': 0})

@app.route('/update-rating', methods=['POST'])
def update_rating():

    user = User.query.get(session['user'])
    movie = movie.query.get(int(request.form.get('movie')))
    score = request.form.get('score')

@app.route('/user/<user_id>')
def display_user_profile(user_id):

    user = User.query.get(user_id)


    return render_template('user_profile.html', user=user)


@app.route('/user/<user_id>/discover')
def display_discoverables(user_id):

    user = User.query.get(user_id)

    return render_template('discover.html', user=user)




# # # # # # # #
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()

###### TO DO:
###### exception handling
