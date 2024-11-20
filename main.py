import subprocess
from flask import Flask, render_template, request, redirect, url_for, flash
import re
app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a strong secret key for sessions

#get the hostname of the system

# Utility function to run system commands
import re

def is_valid_username(username):
    return re.match(r'^[a-zA-Z0-9_-]+$', username) is not None

def is_valid_name(name):
    return re.match(r'^[a-zA-Z\s]+$', name) is not None

def is_valid_email(email):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email) is not None

def run_command(command, input_text=None):
    try:
        result = subprocess.run(
            command,
            input=input_text,
            text=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.stderr.strip())
def get_hostname():
    return run_command(["hostname"])
# Route for managing Samba users
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", hostname=hostname)

# Route for adding a new Samba user
@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")

        # Input validation
        if not is_valid_username(username):
            flash("Invalid username. Only letters, numbers, underscores, and dashes are allowed.", "error")
            return redirect(url_for("add_user"))
        
        if not is_valid_name(first_name) or not is_valid_name(last_name):
            flash("Invalid name. Only letters and spaces are allowed.", "error")
            return redirect(url_for("add_user"))

        if not is_valid_email(email):
            flash("Invalid email address.", "error")
            return redirect(url_for("add_user"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("add_user"))

        try:
            # Create the system account
            run_command(["sudo", "useradd", "-m", username])

            # Set the full name for the user
            run_command(["sudo", "usermod", "-c", f"{first_name} {last_name}", username])

            # Set the Samba password
            run_command(
                ["sudo", "smbpasswd", "-a", username],
                input_text=f"{password}\n{password}\n"
            )

            # Log the email (optional)
            with open("/etc/samba/user_emails.txt", "a") as f:
                f.write(f"{username},{email}\n")

            flash(f"User {username} added successfully!", "success")
        except RuntimeError as e:
            flash(f"Error: {e}", "error")

        return redirect(url_for("home"))

    return render_template("add_user.html")

# Route for changing the password
@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password:
            flash("Username and password are required", "error")
            return redirect(url_for("change_password"))

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("change_password"))

        try:
            # Change the system account password
            run_command(
                ["sudo", "passwd", username],
                input_text=f"{password}\n{password}\n"
            )

            # Change the Samba password
            run_command(
                ["sudo", "smbpasswd", "-a", username],
                input_text=f"{password}\n{password}\n"
            )

            flash(f"Password for {username} updated successfully!", "success")
        except RuntimeError as e:
            flash(f"Error: {e}", "error")

        return redirect(url_for("home"))

    return render_template("change_password.html")

if __name__ == "__main__":
    hostname = get_hostname()

    app.run(host="0.0.0.0", port=5000)
