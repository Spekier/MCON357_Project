from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
import smtplib
from email.mime.text import MIMEText
import schedule
import time
from threading import Thread
from datetime import datetime, timedelta
from . import db  # Import your database instance
from .models import User  # Import your User model

main = Blueprint('main', __name__)

# Gmail account details (keep these secure in a real application)
SENDER_EMAIL = "mcoo275module9@gmail.com"
SENDER_PASSWORD = "tqzp gzdw oawb piab"

def send_email(receiver_email, subject, body):
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        message = MIMEText(body)
        message['Subject'] = subject
        message['From'] = SENDER_EMAIL
        message['To'] = receiver_email
        server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())
        server.quit()
        print(f"Email sent to {receiver_email}: {subject}")
        return True
    except Exception as e:
        print(f"Error sending email to {receiver_email}: {e}")
        return False

def schedule_reminder_task(user_email, event_text, reminder_time):
    now = datetime.now()
    if reminder_time > now:
        time_difference = (reminder_time - now).total_seconds()
        def job():
            send_email(user_email, "Reminder: Upcoming Event", f"This is a reminder for your event: {event_text}")
        schedule.every().second.do(job).at(datetime.fromtimestamp(reminder_time.timestamp()).strftime("%H:%M:%S"))
        print(f"Scheduled reminder for {user_email} at {datetime.fromtimestamp(reminder_time.timestamp())}")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/schedule_reminder', methods=['POST'])
@login_required
def schedule_reminder():
    data = request.get_json()
    event_datetime_unix = data.get('eventDateTime')
    event_text = data.get('eventText')
    reminder_timings = data.get('reminderTimings', [])
    # date_str = data.get('dateStr')
    # event_index = data.get('eventIndex')

    user_email = current_user.email
    event_datetime = datetime.fromtimestamp(event_datetime_unix)
    now = datetime.now()

    for hours_before in reminder_timings:
        reminder_time = event_datetime - timedelta(hours=hours_before)
        if reminder_time > now:
            schedule_reminder_task(user_email, event_text, reminder_time)

    return jsonify({'success': True})
