"""Movie Ratings."""

from jinja2 import StrictUndefined
import json

# from flask.ext.sqlalchemy import SQLAlchemy
# from sqlalchemy import exc

from flask import Flask, render_template, request, redirect, session, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension

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


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
