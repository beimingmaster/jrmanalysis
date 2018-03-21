#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: beimingmaster@gmail.com

import time

from handler import app
from flask import request, jsonify
from common import tool
from common import config

@app.route('/v1/api/debug/info', methods=['GET'])
def debug_info():
	token = None
	if 'token' in request.args:
		token = request.args['token']
	if token == 'admin_token_8':
		result = {'users': config.users, 'tokens': config.tokens, 'tasks': config.tasks}
		return jsonify(result)
	else:
		result = {'code': -1, 'msg': 'invalid token'}
		return jsonify(result)
