import sqlite3
from functools import wraps
from forms import AddTaskForm

from flask import Flask, request, session, render_template, flash, redirect, url_for, g

app = Flask(__name__)
app.config.from_object("_config")

def db_connect():
	return sqlite3.connect(app.config["DATABASE_PATH"])

def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if "logged_in" in session:
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

@app.route("/tasks")
@login_required
def tasks():
	with db_connect() as connection:
		cursor = connection.cursor()

		cursor.execute('''SELECT name, due_date, priority, task_id FROM tasks WHERE status=1''')
		open_tasks = [{"name":task[0], "due_date":task[1], "priority":task[2], "task_id":task[3]} for task in cursor.fetchall()]

		cursor.execute('''SELECT name, due_date, priority, task_id FROM tasks WHERE status=0''')
		closed_tasks = [{"name":task[0], "due_date":task[1], "priority":task[2], "task_id":task[3]} for task in cursor.fetchall()]

	return render_template('tasks.html', form=AddTaskForm(request.form), open_tasks=open_tasks, closed_tasks=closed_tasks)

@app.route("/add", methods=["POST"])
@login_required
def new_task():
	name = request.form["name"]
	due_date = request.form["due_date"]
	priority = request.form["priority"]
	if not name or not due_date or not priority:
		flash("All field are required, try again")
		return redirect(url_for("tasks"))
	else:
		with db_connect() as connection:
			cursor = connection.cursor()
			cursor.execute('''INSERT INTO tasks (name, due_date, priority, status) VALUES (?, ?, ?, 1)''', [name, due_date, priority])
		flash("New task has been added")
		return redirect(url_for("tasks"))

@app.route("/complete/<int:task_id>")
@login_required
def complete(task_id):
	with db_connect() as connection:
		cursor = connection.cursor()
		cursor.execute('''UPDATE tasks SET status=0 WHERE task_id='''+str(task_id))
	flash("The task was marked as complete")
	return redirect(url_for("tasks"))

@app.route("/delete/<int:task_id>")
@login_required
def delete_entry(task_id):
	with db_connect() as connection:
		cursor = connection.cursor()
		cursor.execute('''DELETE FROM tasks WHERE task_id='''+str(task_id))
	flash("The task was deleted")
	return redirect(url_for("tasks"))