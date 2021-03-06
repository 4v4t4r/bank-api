#!/usr/bin/env python
from app import bcrypt, db
from app.models import *
from random import SystemRandom

try:
	# Initalize DB
	db.drop_all()
	db.create_all()

	# Create the general staff user
	hashpw = bcrypt.generate_password_hash("lockdown_staffpw")
	user = User("staff", hashpw, is_staff=True)
	account_main = Account("0000001337", user, balance=1000000000.00, pin=1426180)
	db.session.add(user)
	db.session.add(account_main)

	# Create the scoring engine user
	hashpw = bcrypt.generate_password_hash("9815405C45D69BA8E252")
	user = User("scoring", hashpw, is_staff=True)
	account_main = Account("3141592653", user, balance=0.00, pin=917889)
	db.session.add(user)
	db.session.add(account_main)

	# Create the team accounts
	TEAM_INITIAL_AMOUNT = 85000.00
	TEAM_PASSWORDS = {
		1: 'changeme',
		2: 'changeme',
		3: 'changeme',
		4: 'changeme',
		5: 'changeme',
		6: 'changeme',
		7: 'changeme',
		8: 'changeme',
		9: 'changeme',
		10: 'changeme',
	}

	for teamnum, password in TEAM_PASSWORDS.items():
		accnum = str(''.join(map(str, [SystemRandom().randrange(9) for i in range(10)])))
		pin = int(str(''.join(map(str, [SystemRandom().randrange(9) for i in range(4)]))))

		print "Team %d: ACCNUM: %s / PIN: %d" % (teamnum, accnum, pin)

		user = User("team%d" % int(teamnum), bcrypt.generate_password_hash(password))
		account_main = Account(accnum, user, balance=TEAM_INITIAL_AMOUNT, pin=pin)
		db.session.add(user)
		db.session.add(account_main)
	
	db.session.commit()

	print "BankAPI\n"
	print "Username: admin\nPassword: admin\n"
	print "Account: %s\nBalance: %.2f\nPIN: %d" % (account_main.id, account_main.balance, account_main.pin)
except Exception as e:
	print "Error: %s" % (e)