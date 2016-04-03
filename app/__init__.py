import os
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from flask import Flask, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object('config')

# Setup extensions
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# Setup scheduler
scheduler = BackgroundScheduler()

# Add all the models
from app import models

########################
# Configure Secret Key #
########################
def install_secret_key(app, filename='secret_key'):
	"""
	Configure the SECRET_KEY from a file in the instance directory.

	If the file does not exist, print instructions to create it from
	a shell with a random key, then exit
	"""
	filename = os.path.join(app.instance_path, filename)

	try:
		app.config['SECRET_KEY'] = open(filename, 'rb').read()
	except IOError:
		print('Error: No secret key. Create it with:')
		full_path = os.path.dirname(filename)
		if not os.path.isdir(full_path):
			print('mkdir -p {filename}'.format(filename=full_path))
		print('head -c 24 /dev/urandom > {filename}'.format(filename=filename))
		sys.exit(1)

if not app.config['DEBUG']:
	install_secret_key(app)

##########################
# Utility function to    #
# return a JSON Response #
##########################
def respond(message, data={}, code=200):
	response = {
		'code': code,
		'message': message
	}

	if data:
		response.update(data)

	return jsonify(response)

##########################
# Utility function to    #
# return check all POST  #
# params                 #
##########################
def check_params(request, params):
	missing = []
	for param in params:
		if param not in request.form.keys():
			missing.append(param)

	if missing:
		raise StandardError("You are missing the following paramaters: %s" % ', '.join(missing))

##########################
# Utility function to    #
# validate a session     #
##########################
def validate_session(session):
	session = models.Session.query.filter(models.Session.session == session).first()

	if not session:
		raise StandardError("Invalid or expired session!")

	return session.user

##########################
# Clear out all sessions #
# that are 15 minutes old#
##########################

@scheduler.scheduled_job('cron', id='cleanup_sessions', second=0)
def cleanup_sessions():
	print "[CRON] Cleaning up sessions..."
	try:
		ago = datetime.utcnow() - timedelta(minutes=15)

		num = models.Session.query.filter(models.Session.time < ago).delete()
		db.session.commit()

		print "[CRON] Cleaned up %d old sessions" % (num)
	except Exception as e:
		print e
		db.session.rollback()

		print "[CRON] Failure - rollback triggered"

# Grab all the views
from app.views import main, user, transaction
