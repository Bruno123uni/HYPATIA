import os
import random
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session,url_for, send_file
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
from datetime import datetime
from base64 import b64encode
import base64
from io import BytesIO #Converts data from Database into bytes


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")



Session(app)
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///main.db")


@app.route('/')
def index():
  return render_template("index.html")
 
@app.route("/login", methods=["GET", "POST"])
def login():
  session.clear()
  if request.method == "POST":
        # Ensure username was submitted
      if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
      elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for usernam
      rows = db.execute("SELECT * FROM users WHERE username = :name",name=request.form.get("username"))
      print(len(rows))
      if len(rows) == 0:
        role = "mentor"
        rows = db.execute("SELECT * FROM mentors WHERE username = :name",name=request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid name and/or password", 403)
        session["user_id"] = rows[0]["id"]
      else:
        rows = db.execute("SELECT * FROM users WHERE username = :name",name=request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
          return apology("invalid name and/or password", 403)
        role = "user"
        session["user_id"] = rows[0]["id"]
      session["role"] = role
      return render_template("index.html",role=role,login=login)

  else:
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("name"):
            return apology("must provide name", 403)
        if not request.form.get("username"):
            return apology("must provide username", 403)
        role = request.form.get("Role")
        if role == "user":
            rows = db.execute("SELECT username FROM users")
            for row in rows:
                if request.form.get("username") == row["username"]:
                    return apology("This username is already taken", 403)
        if role == "mentor":
            rows = db.execute("SELECT username FROM mentors")
            for row in rows:
                if request.form.get("username") == row["username"]:
                    return apology("This username is already taken", 403)
        if not request.form.get("Email"):
            return apology("must provide Email", 403)# Ensure inputs was submitted
        if not request.form.get("age"):
            return apology("must provide age", 403)
        if not request.form.get("Interest"):
            return apology("must provide interest", 403)
        if not request.form.get("password"):
            return apology("must provide password", 403)
        if not request.form.get("confirmation"):
            return apology("must provide input", 403)
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("The passwords must match", 403)
        name = request.form.get("name")
        username = request.form.get("username")
        age = request.form.get("age")
        interest = request.form.get("Interest")
        Email = request.form.get("Email")
        password = generate_password_hash(request.form.get("password"))
        if role == "user":
            db.execute("INSERT INTO users (name, password,Email,age, username, field) VALUES (:username, :passw,:e,:s, :k, :a)", username=name, passw=password,e=Email,s=age, k = username, a = interest)
            return redirect("/login")
        else:
            db.execute("INSERT INTO mentors (name, password,Email,age, username, field) VALUES (:username, :passw,:e,:s, :k, :a)", username=name, passw=password,e=Email,s=age, k = username, a = interest)
            rows = db.execute("SELECT * FROM mentors WHERE username = :name",name=username)
            session["user_id"] = rows[0]["id"]
            session['username'] = username
            return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
    
@app.route("/Opp")
def opp():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM opportunities")
        return render_template("opp.html",rows=rows)
    else:
        rows = db.execute("SELECT * FROM opportunities")
        if request.form.get("field"):
            field=request.form.get("field")
            rows = db.execute("SELECT * FROM opportunities WHERE Field=:t",t=field)
        return render_template("opp.html",rows=rows)
@app.route("/mentor")
def m():
    if request.method == "GET":
        inaa = db.execute("SELECT field FROM users WHERE id = :i",i = session["user_id"])
        rows = db.execute("SELECT * FROM mentors WHERE field=:f", f = inaa)
        return render_template("mentors.html",rows=rows)
@app.route("/ng")
def ngos():
    if request.method == "GET":
        rows = db.execute("SELECT * FROM NGO")
        return render_template("ngos.html",rows=rows)
    