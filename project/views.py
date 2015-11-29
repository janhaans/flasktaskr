import sqlite3
from functools import wraps

from flask import Flask, request, session, render_template, flash, redirect, url_for

app = Flask(__name__)
app.config.from_object("_config")

def db_connect():
	return sqlite3.connect(app.config["DATABASE_PATH"])

def login_required(test):
	@wraps
	def wrap(*args, **kwargs):
		if "logged-in" in session:
			return test(*args, **kwargs)
		else:
			flash("Login is required")
			return redirect(url_for('login'))
	return wrap

@app.route("/logout")
def logout():
	session.pop("logged_in", None)
	flash("Goodbye")
	return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def login():
	if request.method=="POST":
		if request.form["username"]==app.config["USER"] and request.form["password"]==app.config["PASSWORD"]:
			session["logged_in"] = True
			flash("Welcome")
			return redirect(url_for("tasks"))
		else:
			error = "Invalid credentials, please try again"
			return render_template("login.html", error=error)
	return render_template("login.html")




