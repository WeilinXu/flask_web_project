import os
import sys
import click

from flask import Flask, render_template
from flask import request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin	# helpful for login
from werkzeug.security import generate_password_hash, check_password_hash	# helpful for login password


prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev'	# required for flash

db = SQLAlchemy(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))  
    return user

# not allow seeing some part of html without login
login_manager.login_view = 'login'
# login_manager.login_message = 'Your custom message'


# initialize the .db file in terminal, run by: flask initdb
@app.cli.command() 
@click.option('--drop', is_flag=True, help='Create after drop.') 
def initdb(drop):
    """Initialize the database."""
    if drop:  
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


# save db data in terminal, run by: flask forge 
@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()
    
    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    
    db.session.commit()
    click.echo('Done.')


# create admin account in terminal
@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')


# use SQLite
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 	# primary key 
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))  # user name
    password_hash = db.Column(db.String(128))  # password
    def set_password(self, password):  
        self.password_hash = generate_password_hash(password)  # set password

    def validate_password(self, password):  # check whether input is true password
        return check_password_hash(self.password_hash, password)
				


class Movie(db.Model):		# entity
    id = db.Column(db.Integer, primary_key=True)  # primary key
    title = db.Column(db.String(60))  # movie title (other attribute)
    year = db.Column(db.String(4))  # movie year


# global variable required for multiple templates
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)	# similar to return {'user': user}


@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# add db data
# about db:
#	access: 	Movie.query.first()
#			Movie.query.get(N)	# get the data with primary key as N
#	access all: 	Movie.query.all()
#	count number of data: Movie.query.count()
#	filter data: 	Movie.query.filter_by(title='Mahjong').first()
#			Movie.query.filter(Movie.title=='Mahjong').first()
#	add data:	db.session.add(movie)
#	delete data:	db.session.delete(movie)
#	commit all changes: db.session.commit() 
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')	# get request from textbox in index.html
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 60:	# invalid
            flash('Invalid input.')
            return redirect(url_for('index'))
        # update back-end
	movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')	# display in index.html by get_flashed_messages()
        return redirect(url_for('index'))	# redirect back to frontend

    # user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)	# user = user,

# edit db data
# index.html-> /movie/edit/<int:movie_id> (new page) ->index.html
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required			# this page requires login
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))
        
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))	# redirect back to frontend
	
    return render_template('edit.html', movie=movie) 

# delete db item, use form rather using new link like edit
# index.html-> /movie/delete/<int:movie_id> (no new page) ->index.html
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required			# this page requires login
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


# result username
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        user = User.query.first()
        user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')



# user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']	# get input of form

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        
        user = User.query.first()
        # check whether 
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))  # go to page after login

        flash('Invalid username or password.')  # if password is wrong
        return redirect(url_for('login'))  # go back to login page
    
    return render_template('login.html')


# user logout
@app.route('/logout')
@login_required			# this page requires login
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))

'''
name = 'Khan'
movies = [
    {'title': 'My Neighbor Totoro', 'year': '1988'},
    {'title': 'Dead Poets Society', 'year': '1989'},
    {'title': 'A Perfect World', 'year': '1993'},
    {'title': 'Leon', 'year': '1994'},
    {'title': 'Mahjong', 'year': '1996'},
    {'title': 'Swallowtail Butterfly', 'year': '1996'},
    {'title': 'King of Comedy', 'year': '1999'},
    {'title': 'Devils on the Doorstep', 'year': '1999'},
    {'title': 'WALL-E', 'year': '2008'},
    {'title': 'The Pork of Music', 'year': '2012'},
]


@app.route('/hello')
def hello():
    return 'Hello'

@app.route('/user/<name>')	# url with input parameter
def user_page(name):
    return 'User: %s' % name

@app.route('/test')
def test_url_for():
    print(url_for('hello'))  
    print(url_for('user_page', name='khan')) 	# print result of function user_page with input khan 
    print(url_for('user_page', name='peter')) 
    print(url_for('test_url_for'))  
    print(url_for('test_url_for', num=2))
    return 'Test page'

@app.route('/')
def index():
    return render_template('index.html', name=name, movies=movies)	# sent value of name and movies to index.html
'''
