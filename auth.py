import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
class User:
    def __init__(self, id, username, role):
        self.id       = id
        self.username = username
        self.role     = role
    
    def is_authenticated(self): return True
    def is_active(self):        return True
    def is_anonymous(self):     return False
    def get_id(self):           return str(self.id)

bcrypt = Bcrypt()
auth   = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        conn = sqlite3.connect("surveillance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, role, password_hash FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.check_password_hash(user[2], password):
            login_user(User(id=user[0], username=username, role=user[1]))  # Log in using user ID
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("auth.login"))
    else:
        return render_template("login.html")
    
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email    = request.form.get("email")
        password = request.form.get("password")
        role     = request.form.get("role", "viewer")  # default to viewer if not specified
        
        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        
        conn = sqlite3.connect("surveillance.db")
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (username, email, password_hash, role)
            )
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except sqlite3.IntegrityError:
            flash("Username or email already exists", "danger")
            return redirect(url_for("auth.register"))
        finally:
            conn.close()
    else:
        return render_template("register.html")