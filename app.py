from flask import Flask, render_template, request, redirect, url_for, flash, session
import csv
import os
from dotenv import load_dotenv
import random
import requests


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ==== Laundry Request ====
@app.route('/request', methods=['GET', 'POST'])
def laundry_request():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        service_type = request.form['service_type']
        cloth_type = request.form['cloth_type']
        quantity = request.form['quantity']
        pickup_method = request.form['pickup_method']
        datetime = request.form['datetime']
        instructions = request.form['instructions']

        # CSV path
        folder_path = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, 'laundry_requests.csv')

        file_exists = os.path.exists(file_path)

        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Name', 'Phone', 'Address', 'Service', 'Cloth Type',
                                 'Quantity', 'Pickup Method', 'Date/Time', 'Instructions'])
            writer.writerow([name, phone, address, service_type, cloth_type,
                             quantity, pickup_method, datetime, instructions])

        flash("Your request has been submitted successfully!", "success")
        return redirect(url_for('laundry_request'))

    return render_template('request.html')

# ==== Admin Login ====
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    session.pop('admin_logged_in', None)  # Always ask for login again
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin_user = os.getenv("ADMIN_USERNAME")
        admin_pass = os.getenv("ADMIN_PASSWORD")

        if username == admin_user and password == admin_pass:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Try again.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

# ==== Admin Dashboard ====
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash("Login required to access dashboard.", "warning")
        return redirect(url_for('admin_login'))

    # Load laundry request data
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'laundry_requests.csv')
    records, headers = [], []
    if os.path.exists(file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader, [])
            records = list(reader)

    # Load feedback data
    feedback_file = os.path.join(os.path.dirname(__file__), 'data', 'feedback.csv')
    feedbacks = []
    if os.path.exists(feedback_file):
        with open(feedback_file, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            feedbacks = list(reader)

    return render_template('dashboard.html', headers=headers, records=records, feedbacks=feedbacks)

# ==== Admin Logout ====
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('admin_login'))

# ==== Feedback Save ====
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        message = request.form['message']

        folder = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, 'feedback.csv')
        file_exists = os.path.exists(file_path)

        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Name', 'Phone', 'Message'])
            writer.writerow([name, phone, message])

        flash("Thank you for your feedback!", "success")
        return redirect(url_for('feedback'))

    return render_template('feedback.html')

        
# ==== Other Pages ====
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/rates')
def rates():
    return render_template('rates.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)