#!/usr/bin/env python2.7
import os, base64
from hashlib import sha256
from hmac import HMAC
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, url_for
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


@app.route('/snc', methods = ['GET', 'POST'])
@login_required
def snc():

  snacks = []
  if bool(request.form):
    Name = request.form['sname'] if request.form['sname'] else None
    Type = request.form['type'] if request.form['type'] else None
    Manu = request.form['manu'] if request.form['manu'] else None

    cursor = g.conn.execute("SELECT * FROM snack WHERE (%s is null OR sname ~ \'%s*\') AND (%s is null OR type = %s) AND (%s is null or manufacturer ~ \'%s\')", Name, Name, Type, Type, Manu, Manu)
    snacks = cursor.fetchall()
    cursor.close()  

  else:
    cursor = g.conn.execute("SELECT * FROM snack")
    snacks = cursor.fetchall()
    cursor.close()

# Comments for all
  comments = []

  cursor = g.conn.execute("SELECT S.bid, R.grades, C.description, to_char(C.p_date, 'Month DD, YYYY'), U.u_name FROM snack S, rate R, comment C, suser U WHERE S.bid = R.bid AND R.bid = C.bid and U.uid = C.uid ORDER BY R.review_date DESC")
  comments = cursor.fetchall()
  cursor.close()

# Query Average grades for every snack
  grades = []

  cursor = g.conn.execute("SELECT S.bid, ROUND(AVG(R.rate),2) FROM snack S, rate R WHERE S.bid = R.bid GROUP BY S.bid")
  grades = cursor.fetchall()
  cursor.close()

# Query this user's comments
  user_comments = []

  cursor = g.conn.execute("SELECT DISTINCT S.bid, R.grades, C.description, to_char(C.p_date, 'Month DD, YYYY') FROM snack S, rate R WHERE S.bid = R.bid AND C.uid=%s AND R.uid=%s", current_user.uid, current_user.uid)
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
      return render_template('snc.html')
    else:
      error = "existed username."

  return render_template('register.html', error=error)


def register_user(user):
  cursor = g.conn.execute("INSERT INTO suser (uid, u_name, location, email, phone, password) VALUES (%s, %s,%s, %s, %s, %s)", ('11', user.username, user.location, user.email, user.phone, encrypt_pwd(user.password)))

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
def load_user(username):
  cursor = g.conn.execute("SELECT * FROM suser WHERE u_name=%s", username)
  data = cursor.fetchone()
  cursor.close()

  if data is None:
    return None

  return User(data[1], data[2], data[3], data[4], data[5], data[0])

def valid_user(user):
  cursor = g.conn.execute("SELECT * FROM suser WHERE u_name=%s", user.username)
  data = cursor.fetchone()
  cursor.close()

  return valid_pwd(str(user.password), str(data[2]))

@app.route('/login', methods=['POST'])
def login():
  user = User(request.form['username'], request.form['password'])
  if valid_user(user):
    login_user(user)
    return render_template('snc.html')
  
  return render_template('login.html', error='Invalid username or password.')


def encrypt_pwd(pwd, salt=None):
  if salt is None:
    salt = os.urandom(8)
  
  assert 8==len(salt)
  assert isinstance(salt, str)

  pwd =  pwd.encode('UTF-8')
  
  result = pwd
  for i in xrange(10):
    result = HMAC(result, salt, sha256).digest()


  return (salt + result).encode('hex')

def valid_pwd(hashed, input_pwd):
  return hashed == encrypt_pwd(input_pwd, salt = hashed[:8])



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
