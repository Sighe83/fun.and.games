"""
Aula Weekly Notes Web Application
Simple Flask app for viewing weekly notes from Aula
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from aula_client import AulaClient
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate random secret key for sessions

# Store client instances per session
clients = {}


def get_client():
    """Get or create AulaClient for current session"""
    session_id = session.get('session_id')
    if session_id and session_id in clients:
        return clients[session_id]
    return None


@app.route('/')
def index():
    """Home page - redirect to login or weekly notes"""
    client = get_client()
    if client and client.logged_in:
        return redirect(url_for('weekly_notes'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Indtast både brugernavn og adgangskode', 'error')
            return render_template('login.html')

        # Create new client and attempt login
        client = AulaClient()

        try:
            if client.login(username, password):
                # Create session ID and store client
                session_id = os.urandom(16).hex()
                session['session_id'] = session_id
                clients[session_id] = client

                flash('Login lykkedes!', 'success')
                return redirect(url_for('weekly_notes'))
            else:
                flash('Login mislykkedes. Tjek brugernavn og adgangskode.', 'error')
        except Exception as e:
            flash(f'Der opstod en fejl under login: {str(e)}', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout - clear session"""
    session_id = session.get('session_id')
    if session_id and session_id in clients:
        del clients[session_id]
    session.clear()
    flash('Du er nu logget ud', 'info')
    return redirect(url_for('login'))


@app.route('/weekly-notes')
def weekly_notes():
    """View weekly notes for current and next week"""
    client = get_client()

    if not client or not client.logged_in:
        flash('Du skal være logget ind for at se ugenoter', 'error')
        return redirect(url_for('login'))

    try:
        # Get children info
        children = client.get_children_info()

        # Get current week and next week notes
        current_week = client.get_weekly_notes(week_offset=0)
        next_week = client.get_weekly_notes(week_offset=1)

        return render_template(
            'weekly_notes.html',
            children=children,
            current_week=current_week,
            next_week=next_week
        )
    except Exception as e:
        flash(f'Der opstod en fejl ved hentning af ugenoter: {str(e)}', 'error')
        return redirect(url_for('login'))


@app.template_filter('format_datetime')
def format_datetime(value):
    """Format datetime string for display"""
    if not value:
        return ''
    try:
        # Parse ISO format datetime
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return value


@app.template_filter('format_date')
def format_date(value):
    """Format date string for display"""
    if not value:
        return ''
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y')
    except:
        return value


@app.template_filter('weekday')
def weekday_filter(value):
    """Get weekday name from date"""
    if not value:
        return ''
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        weekdays = ['Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag', 'Søndag']
        return weekdays[dt.weekday()]
    except:
        return ''


if __name__ == '__main__':
    print("Starting Aula Weekly Notes application...")
    print("Open browser to: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
