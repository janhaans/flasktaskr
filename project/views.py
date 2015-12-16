from functools import wraps
from forms import AddTaskForm, RegisterForm, LoginForm

from flask import Flask, request, session, render_template, flash, redirect, url_for

from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object("_config")
db = SQLAlchemy(app)

from models import Task, User

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
	open_tasks = db.session.query(Task).filter_by(status="1").order_by(Task.due_date.asc())
	closed_tasks = db.session.query(Task).filter_by(status="0").order_by(Task.due_date.asc())
	return render_template('tasks.html', form=AddTaskForm(request.form), open_tasks=open_tasks, closed_tasks=closed_tasks)

@app.route("/add", methods=["GET", "POST"])
@login_required
def new_task():
	form = AddTaskForm(request.form)
	if request.method == "POST":
		if form.validate_on_submit():
			new_task = Task(form.name.data, form.due_date.data, form.priority.data, 1)
			db.session.add(new_task)
			db.session.commit()
			flash("New task has been added")
	return redirect(url_for("tasks"))

@app.route("/register", methods=["GET", "POST"])
def register():
	error = None
	form = RegisterForm()
	if form.validate_on_submit():
		new_user = User(form.username.data, form.email.data, form.password.data)
		db.session.add(new_user)
		db.session.commit()
		flash("New user has been registered")
		return redirect(url_for("login"))
	return render_template('register.html', form=form, error=error)



@app.route("/complete/<int:task_id>")
@login_required
def complete(task_id):
	new_id = task_id
	db.session.query(Task).filter_by(task_id=new_id).update({"status":0})
	db.session.commit()
	flash("The task was marked as complete")
	return redirect(url_for("tasks"))

@app.route("/delete/<int:task_id>")
@login_required
def delete_entry(task_id):
	delete_task = task_id
	db.session.query(Task).filter_by(task_id=delete_task).delete()
	db.session.commit()
	flash("The task was deleted")
	return redirect(url_for("tasks"))