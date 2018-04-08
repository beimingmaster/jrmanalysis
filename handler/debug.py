#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: beimingmaster@gmail.com

import os
import time

from handler import app
from flask import request, jsonify, send_from_directory
from common import tool
from common import config

@app.route('/data/<path:path>')
def send_data(path):
	#print('path: %s' % path)
	root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/")
	#print('root: %s' % root)
	return send_from_directory(root, path)

@app.route('/v1/api/debug/info', methods=['GET'])
def debug_info():
	token = None
	if 'token' in request.args:
		token = request.args['token']
	if token == config.admin_token:
		result = {'users': config.users, 'tokens': config.tokens, 'tasks': config.tasks}
		return jsonify(result)
	else:
		result = {'code': -1, 'msg': 'invalid token'}
		return jsonify(result)
