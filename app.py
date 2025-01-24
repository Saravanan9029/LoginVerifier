from flask import Flask, render_template, request, jsonify
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

app = Flask(__name__)

# Store OTP temporarily (in production, use a database)
otp_storage = {}
otp_expiry = 300  # OTP expiry time (5 minutes)

# Function to send OTP via email
def send_otp_email(to_email, otp):
    from_email = "your-email@gmail.com"
    from_password = "your-email-password"
    
    # Set up the server
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(from_email, from_password)

    # Create the email
    subject = "Your OTP Code"
    body = f"Your OTP code is {otp}. It will expire in 5 minutes."
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    # Send the email
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

@app.route('/')
def index():
    return render_template('login.html')  # Serve the login.html from the templates folder

@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data['email']
    
    # Generate a random OTP
    otp = random.randint(100000, 999999)
    otp_storage[email] = {'otp': otp, 'expiry': time.time() + otp_expiry}
    
    # Send OTP to the email
    send_otp_email(email, otp)
    
    return jsonify({'success': True})

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    otp = int(data['otp'])
    
    # Check if OTP exists and is valid
    for email, otp_data in otp_storage.items():
        if otp_data['otp'] == otp and otp_data['expiry'] > time.time():
            # OTP is valid and hasn't expired
            del otp_storage[email]  # Delete OTP after successful login
            return jsonify({'success': True})
    
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(debug=True)
