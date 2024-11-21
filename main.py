import subprocess
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
import re
from psutil import disk_usage, disk_io_counters, net_io_counters
app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a strong secret key for sessions

#get the hostname of the system

# Utility function to run system commands
import re
# Function to fetch system metrics
def get_system_metrics():
    # Disk usage
    p_disk_usage = disk_usage('/')
    total_storage = p_disk_usage.total // (1024 ** 3)  # Convert to GB
    used_storage = p_disk_usage.used // (1024 ** 3)
    free_storage = p_disk_usage.free // (1024 ** 3)
    
    # Disk I/O activity
    p_disk_io = disk_io_counters()
    read_bytes = p_disk_io.read_bytes // (1024 ** 2)  # Convert to MB
    write_bytes = p_disk_io.write_bytes // (1024 ** 2)
    
    # Network activity
    p_net_io = net_io_counters()
    bytes_sent = p_net_io.bytes_sent // (1024 ** 2)  # Convert to MB
    bytes_recv = p_net_io.bytes_recv // (1024 ** 2)
    
    return {
        "total_storage": total_storage,
        "used_storage": used_storage,
        "free_storage": free_storage,
        "read_bytes": read_bytes,
        "write_bytes": write_bytes,
        "bytes_sent": bytes_sent,
        "bytes_recv": bytes_recv,
    }
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
    # Fetch system metrics
    metrics = get_system_metrics()
    return render_template("index.html", metrics=metrics)

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

            #set the email address for the user
            run_command(["sudo", "usermod", "-c", f"{email}", username])

            # Set the Samba password
            run_command(
                ["sudo", "smbpasswd", "-a", username],
                input_text=f"{password}\n{password}\n"
            )



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
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password:
            flash("Username and password are required", "error")
            return redirect(url_for("change_password"))

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("change_password"))

        try:
            # Get current email from the system
            current_email = run_command(["sudo", "getent", "passwd", username]).split(":")[4].strip()

            # If email is not set or mismatches, flash a warning
            if not current_email or current_email.lower() == "n/a":
                current_email = None  # Email not set
            elif current_email.strip() != email.strip():
                flash("The provided email does not match the system's records", "error")
                return redirect(url_for("change_password"))

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

            # Prompt to add email if it's not set
            if not current_email:
                flash("Email not set for this user. Please add an email address.", "warning")
                return redirect(url_for("add_email", username=username))

        except RuntimeError as e:
            flash(f"Error: {e}", "error")

        return redirect(url_for("home"))

    return render_template("change_password.html")

# Route for adding an email to an existing user
@app.route("/add_email/<username>", methods=["GET", "POST"])
def add_email(username):
    if request.method == "POST":
        email = request.form.get("email")

        if not email:
            flash("Email is required", "error")
            return redirect(url_for("add_email", username=username))

        try:
            # Update the user's comment field with the email
            run_command(["sudo", "usermod", "-c", f"{email}", username])
            flash(f"Email added for user {username} successfully!", "success")
        except RuntimeError as e:
            flash(f"Error: {e}", "error")

        return redirect(url_for("home"))

    return render_template("add_email.html", username=username)
@app.route("/api/system_metrics", methods=["GET"])
def system_metrics_api():
    metrics = get_system_metrics()
    return jsonify(metrics)

if __name__ == "__main__":
    hostname = get_hostname()

    app.run(host="0.0.0.0", port=8089)
