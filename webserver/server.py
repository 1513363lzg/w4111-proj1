
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import numpy as np

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.75.150.200/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.150.200/proj1part2"
#
DATABASEURI = "postgresql://sy2890:1899@34.75.150.200/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""SELECT * FROM Buildings
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
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
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  # print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT * FROM buildings")
  # building_names = g.conn.execute("select COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'buildings'")
  g.results = cursor.fetchall()
  g.names = ['name','address','zipcode','year','valuation','since','team_name']
  # results={name:[] for name in names}
  # for name in names:
  #   for result in cursor:
  #     results[name].append(result[name])
  cursor.close()
  # building_names.close()

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
  # context = dict(names = cursor)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  # return render_template("index.html", results=zip(*results.values()),names=names)
  return render_template("index.html", results=g.results, names=g.names)
#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/<name>/<address>/<zipcode>')
def building_detail(name,address,zipcode):
  address = address.replace('_',' ')
  commands_apart = f"""select * from apartments_listed 
                    where zipcode in (select zipcode from buildings where zipcode='{zipcode}' and address='{address}')
                    """
  commands_tweets = f"""select t.user_id, t.tweet_time, t.tweet_content, t.sentiment_type from commented c, buildings b, tweets t 
                     where b.zipcode='{zipcode}' and b.address='{address}' and b.zipcode=c.zipcode and b.address=c.address
                     and t.user_id=c.user_id and t.tweet_time=c.tweet_time
                    """
  commands_manager = f"""select * from prospect_manager
                      where team_name in (select team_name from buildings where zipcode='{zipcode}' and address='{address}')"""
  commands_surr = f"""select type_s, count(*) from surroundings
                      where zipcode in (select s.zipcode_s from buildings b,building_surround s where s.zipcode='{zipcode}' and s.address='{address}')
                      group by type_s
                    """
  cursor_a = g.conn.execute(commands_apart)
  cursor_t = g.conn.execute(commands_tweets)
  cursor_m = g.conn.execute(commands_manager)
  cursor_s = g.conn.execute(commands_surr)

  result_a, result_t, result_m , result_s  = cursor_a.fetchall(),cursor_t.fetchall(),cursor_m.fetchall(),cursor_s.fetchall()
  names_a = ['price','apart_number','zipcode','rental','layout','address','by_date']
  names_t = ['user_id','tweet_time','tweet_content','sentiment_type']
  names_m = ['team_name','number_of_employees']
  names_s = ['type_s','Numbers']
  cursor_a.close(),cursor_t.close(),cursor_m.close(),cursor_s.close()

  return render_template("result.html",result_a=result_a,result_t=result_t,result_m=result_m,result_s=result_s,names_a=names_a,names_t=names_t,names_m=names_m,names_s=names_s)

@app.route('/<teamname>')
def manager_detail(teamname):
  comment = f"""select * from tweets where user_id in (select s.user_id from satisfy s, prospect_manager p where p.team_name='{teamname}')"""
  names_t = ['user_id', 'tweet_time', 'tweet_content', 'sentiment_type']
  cursor_t = g.conn.execute(comment)
  result = cursor_t.fetchall()
  cursor_t.close()
  return render_template("tweets.html",result=result,names=names_t)

@app.route('/',methods = ['GET', 'POST'])
def search_buildings():
  if request.method == 'POST':
    name = request.form.get('search')
    commands = f"select * from buildings where name ilike '%%{name}%%' or address ilike '%%{name}%%' or team_name ilike '%%{name}%%'"
    cursor = g.conn.execute(commands)
    results = cursor.fetchall()
    cursor.close()
    names = ['name','address','zipcode','year','valuation','since','team_name']
    return render_template("index.html", results=results, names=names)
  return '''<form method="POST"> What do you want? Please enter keyword: <input type="text" name="search"><br>
                  <input type="submit" value="Go"><br>
                  </form>'''
# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
  app.debug=True
  run()
