#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: beimingmaster@gmail.com

import time

from hashlib import md5
from flask import request
from flask import jsonify
from handler import app
from common import config

@app.route('/v1/api/authorize', methods=['POST'])
def authorize():
	username = None
	password = None
	content_type = request.headers.get('Content-Type')
	if content_type and content_type.startswith('application/x-www-form-urlencoded'):
		username = request.form.get('username', '')
		password = request.form.get('password', '')
	elif content_type and content_type.startswith('application/json'):
		data = request.get_json()
		if data and 'username' in data:
			username = data['username']
		if data and 'password' in data:
			password = data['password'] 
	else:
		pass
	if not username or not password or len(username) < 8 or len(password) < 32:
		result = {'code': 1001, 'msg': 'param invalid'}
		return jsonify(result)
	elif check_user(username, password):
		token, expires_in = get_user_token(username)
		result = {'code': 0, 'msg': 'ok', 'token': token, 'expires_in': expires_in}
		return jsonify(result)
	else:
		result = {'code': 2001, 'msg': 'authorization failed'}
		return jsonify(result)

def check_user(username, password):
	if username in config.users:
		source_password = config.users[username]['password']
		if password == md5(source_password.encode('utf-8')).hexdigest():
			return True
		else:
			return False
	else:
		return False

def get_user_token(username):
	token = md5(('%s-%f' % (username, time.time())).encode('utf-8')).hexdigest()
	expires_in = 3600 * 24 * 30
	expire_time = time.time() + expires_in
	config.users[username]['token'] = token
	config.users[username]['expire_time'] = expire_time
	config.tokens[token] = {'username': username, 'expire_time': expire_time}
	return token, expires_in
