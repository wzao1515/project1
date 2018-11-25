#!/usr/bin/env python2.7
import logging
import os, base64, random
from hashlib import sha256
from datetime import datetime
from hmac import HMAC
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from user import User

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'


# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "jq2282"
DB_PASSWORD = "1dsbj2kr"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():

  if current_user.is_authenticated:
    return redirect(url_for('snc'))
  # DEBUG: this is debugging code to see what request looks like
    print request.args
  #
  # example of a database query
  #
    #cursor = g.conn.execute("SELECT name FROM test")
    #names = []
    #for result in cursor:
     # names.append(result['name'])  # can also be accessed using result[0]
    #cursor.close()
  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
    #context = dict(data = names)
    

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("login.html")


@app.route('/post_comment', methods = ['POST', 'GET'])
@login_required
def post_comment():
	uid = current_user.uid
	p_date = str(datetime.now().date())
	logging.warning(request.form['bid'])
	logging.warning(request.form['text'])
	
	cursor = g.conn.execute("SELECT * from rate where bid=%s AND uid=%s", request.form['bid'], uid)
	s = []
	s = cursor.fetchall()
	cursor.close()
	if s == []:
		res = g.conn.execute("INSERT into rate(uid, grades, bid) values (%s, %s, %s)", uid, request.form['grades'], request.form['bid'])
		res = g.conn.execute("INSERT into comment(uid, bid, p_date, description) values (%s, %s, %s, %s)", uid, request.form['bid'], p_date, request.form['text'])
	else:
		res = g.conn.execute("UPDATE rate set grades=%s WHERE bid=%s AND uid=%s", request.form['grades'], request.form['bid'], uid)
		res = g.conn.execute("UPDATE comment set bid=%s, p_date=%s, description=%s WHERE uid = %s", request.form['bid'], p_date, request.form['text'], uid)
	return redirect('/snc')


@app.route('/U_setting', methods = ['POST', 'GET'])
@login_required
def U_setting():
	us = []
	
	cursor = g.conn.execute("SELECT uid, u_name, location, email, phone from suser WHERE uid=%s", current_user.uid)
	us = cursor.fetchall()	
	cursor.close()
	logging.warning(us)
	noteat = []
	cursor = g.conn.execute("SELECT i_name, uid FROM noteat where uid=%s", current_user.uid)
	noteat = cursor.fetchall()
	cursor.close()

	if bool(request.form):
		cursor = g.conn.execute("SELECT count(*) from noteat where uid=%s", current_user.uid)
		number = cursor.fetchone()
		
		res = g.conn.execute("UPDATE noteat set ")
	else:	
		pass
	context = dict(us=us, noteat=noteat)
	return render_template('U_setting.html', **context)

@app.route('/snc', methods = ['GET', 'POST'])
@login_required
def snc():

	snacks = []
	if bool(request.form):
		Name = request.form['sname'] if request.form['sname'] else ''
		Type = request.form['type'] if request.form['type'] else ''
		Manu = request.form['manu'] if request.form['manu'] else ''
		logging.warning(Name)
		logging.warning(Type)
		logging.warning(Manu)

		if Name == '':
			if Type == '':
				if Manu == '':
					cursor = g.conn.execute("SELECT * FROM snack")
				else:
					cursor = g.conn.execute("SELECT * FROM snack WHERE manufacturer LIKE %s", Manu)
			else:
				if Manu == '':
					cursor = g.conn.execute("SELECT * FROM snack WHERE type=%s", Type)
				else:
					cursor = g.conn.execute("SELECT * FROM snack WHERE type=%s AND manufacturer LIKE %s", Type, Manu)
		else:
			if Type == '':
				if Manu == '':
					logging.warning("just name")
					cursor = g.conn.execute("SELECT * FROM snack WHERE sname LIKE %s", Name.encode("utf-8"))
				else:
					cursor = g.conn.execute("SELECT * FROM snack WHERE manufacturer LIKE %s AND sname LIKE %s", Manu, Name)
			else:
				if Manu == '':
					cursor = g.conn.execute("SELECT * FROM snack WHERE type=%s AND sname LIKE %s", Type, Name)
				else:
					cursor = g.conn.execute("SELECT * FROM snack WHERE type=%s AND manufacturer LIKE %s AND sname LIKE %s", Type, Manu, Name) 
	else:
		#if no search, should show the hot goods
		cursor = g.conn.execute('''	WITH hot_snack(name,type,avg, bid) AS(
	SELECT DISTINCT S1.sname, S1.type, AVG(R1.grades) as avg, S1.bid
	FROM snack S1, rate R1
	WHERE S1.bid=R1.bid
	GROUP BY S1.bid
	HAVING AVG(R1.grades) >= ALL(
			SELECT AVG(R2.grades)
			FROM snack S2, rate R2
			WHERE S2.type=S1.type
			AND S2.bid=R2.bid
			GROUP BY S2.bid
		)
	)
	SELECT S.*
	FROM hot_snack HS, snack S
WHERE HS.bid=S.bid''')
	snacks = cursor.fetchall()
	print snacks
	cursor.close()  

# Comments for all
	comments = []

	cursor = g.conn.execute("SELECT S.bid, U.u_name, R.grades, C.description, to_char(C.p_date, 'Month DD, YYYY') FROM snack S, rate R, comment C, suser U WHERE S.bid = R.bid AND R.uid = U.uid AND R.bid = C.bid and U.uid = C.uid ORDER BY C.p_date DESC")
	comments = cursor.fetchall()
	cursor.close()

# Query Average grades for every snack
	grades = []

	cursor = g.conn.execute("SELECT S.bid, ROUND(AVG(R.grades),2) FROM snack S, rate R WHERE S.bid = R.bid GROUP BY S.bid")
	grades = cursor.fetchall()
	cursor.close()

# Query this user's comments
	user_comments = []

	cursor = g.conn.execute("SELECT DISTINCT S.bid, R.grades, C.description, to_char(C.p_date, 'Month DD, YYYY') FROM comment C, snack S, rate R WHERE S.bid = R.bid AND C.uid=%s AND R.uid=%s", current_user.uid, current_user.uid)
	user_comments = cursor.fetchall()
	cursor.close()

	context = dict(snacks=snacks, comments=comments, grades=grades, user_comments=user_comments)
	return render_template("snc.html", **context)


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'GET':
    return render_template('register.html')

  error = None

  if request.method == 'POST':
    try:
      new_user = User(request.form['username'],
                      request.form['password'],
		      request.form['location'],
		      request.form['phone'],
                      request.form['email'])

    except ValueError as e:
      error = "Username or Password is empty"

    if (not is_registered(new_user)):
      register_user(new_user)
      login_user(new_user)
      return redirect(url_for('snc'))
    else:
      error = "existed username."

  return render_template('register.html', error=error)


def register_user(user):
  cursor = g.conn.execute("INSERT INTO suser (u_name, location, email, phone, password) VALUES (%s,%s, %s, %s, %s)", (user.username, user.location, user.email, user.phone, encrypt_pwd(user.password)))

  cursor.close()

def is_registered(user):
  cursor = g.conn.execute("SELECT * FROM suser WHERE u_name=%s", (user.username))
  data = cursor.fetchone()
  cursor.close()

  if data:
    return True
  else:
    return False

@login_manager.user_loader
def load_user(u_name):
  cursor = g.conn.execute("SELECT * FROM suser WHERE u_name=%s", u_name)
  data = cursor.fetchone()
  cursor.close()

  if data is None:
    return None

  return User(data[1], data[5], data[2], data[4], data[3], data[0])

def valid_user(user):
  cursor = g.conn.execute("SELECT * FROM suser WHERE u_name=%s", user.username)
  data = cursor.fetchone()
  cursor.close()
  if data is None:
    return False

  return valid_pwd(data[4], str(user.password))

@app.route('/login', methods=['POST', 'GET'])
def login():
  if request.method == 'GET':
    return render_template('login.html')
  user = User(request.form['username'], request.form['password'])
  if not user.username:
    flash("Please enter your name")
    return render_template('login.html')

  if not user.password:
    flash("Please enter your password")
    return render_template('login.html')

  if valid_user(user):
    login_user(user)
    return redirect(url_for('snc'))
  
  return render_template('login.html', error='Invalid username or password.')


def encrypt_pwd(pwd, move=None):

  return str(pwd)

def valid_pwd(hashed, input_pwd):
  return hashed==input_pwd


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=4396, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  app.secret_key = os.urandom(12)
  run()
