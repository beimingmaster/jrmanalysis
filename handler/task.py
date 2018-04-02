#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: beimingmaster@gmail.com

import time
import os
from handler import app
from flask import request, jsonify
from common import tool
from common import config

@app.route('/v1/api/task/data/submit', methods=['POST'])
def task_data_submit():
	token = request.headers.get('X-Token')
	if not tool.check_token_valid(token):
		result = {'code': 1002, 'msg': 'token invalid or expired'}
		return jsonify(result)
	task_data = request.get_json()
	if not task_data or not task_data['records']:
		result = {'code': 3001, 'msg': 'data format not correct'}
		return jsonify(result)
	task_id = tool.generate_task_id()
	config.tasks[task_id] = {'token': token, 'status': 'wait'}
	ok = tool.save_task_data(task_id, task_data)
	if not ok:
		result = {'code': -1, 'msg': 'save task data fail'}
		return jsonify(result)
	else:
		result = {'code': 0, 'msg': 'ok', 'task_id': task_id}
		return jsonify(result)

@app.route('/v1/api/task/file/submit', methods=['POST'])
def task_file_submit():
	token = request.headers.get('X-Token')
	if not tool.check_token_valid(token):
		result = {'code': 1002, 'msg': 'token invalid or expired'}
		return jsonify(result)
	task_data = request.get_json()
	if not task_data or not task_data['file_url']:
		result = {'code': 3001, 'msg': 'file url not correct'}
		return jsonify(result)
	task_id = tool.generate_task_id()
	config.tasks[task_id] = {'token': token, 'status': 'wait'}
	ok = tool.save_task_data(task_id, task_data)
	if not ok:
		result = {'code': -1, 'msg': 'save task data fail'}
		return jsonify(result)
	else:
		result = {'code': 0, 'msg': 'ok', 'task_id': task_id}
		return jsonify(result)

@app.route('/v1/api/task/status', methods=['GET'])
def get_task_status():
	token = request.headers.get('X-Token')
	if not tool.check_token_valid(token):
		result = {'code': 1002, 'msg': 'token invalid or expired'}
		return jsonify(result)
	if 'task_id' not in request.args:
		result = {'code': 1001, 'msg': 'param invalid'}
		return jsonify(result)
	task_id = request.args['task_id']
	if task_id not in config.tasks:
		result = {'code': 3002, 'msg': 'task not exist'}
		return jsonify(result)
	else:
		result = {'code': 0, 'msg': 'ok', 'task_id': task_id, 'task_status': config.tasks[task_id]['status']}
		return jsonify(result)

@app.route('/v1/api/task/status', methods=['POST'])
def change_task_status():
	token = request.headers.get('X-Token')
	if not tool.check_token_valid(token):
		result = {'code': 1002, 'msg': 'token invalid or expired'}
		return jsonify(result)
	data = request.get_json()
	if 'task_id' not in data:
		result = {'code': 1001, 'msg': 'no task id'}
		return jsonify(result)
	if 'task_status' not in data:
		result = {'code': 1001, 'msg': 'no task status'}
		return jsonify(result)
	task_id = data['task_id']
	task_status = data['task_status']
	if task_id not in config.tasks:
		result = {'code': 3002, 'msg': 'task not exist'}
		return jsonify(result)
	elif task_status not in ['wait', 'running', 'failed', 'finished']:
		result = {'code': 1001, 'msg': 'task status not correct'}
		return jsonify(result)
	else:
		config.tasks[task_id]['status'] = task_status
		result = {'code': 0, 'msg': 'ok'}
		return jsonify(result)

@app.route('/v1/api/task/result', methods=['GET'])
def get_task_result():
	token = request.headers.get('X-Token')
	if not tool.check_token_valid(token):
		result = {'code': 1002, 'msg': 'token invalid or expired'}
		return jsonify(result)
	if 'task_id' not in request.args:
		result = {'code': 1001, 'msg': 'param invalid'}
		return jsonify(result)
	task_id = request.args['task_id']
	if task_id not in config.tasks:
		result = {'code': 3002, 'msg': 'task not exist'}
		return jsonify(result)
	else:
		task_status = config.tasks[task_id]['status']
		if task_status not in ['failed', 'finished']:
			result = {'code': -1, 'msg': 'task not completed'}
			return jsonify(result)
		else:
			task_result_file = 'task/%s/result.json' % task_id
			if not os.path.exists(task_result_file):
				result = {'code': -1, 'msg': 'task result file not exist'}	
				return jsonify(result)
			else:
				with open(task_result_file, 'r') as f:
					task_result = f.read()
					if not task_result:
						result = {'code': -1, 'msg': 'task result data not exist'}
						return jsonify(result)
					else:
						return task_result
