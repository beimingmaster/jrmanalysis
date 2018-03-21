#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: beimingmaster@gmail.com

import time
import os
import json
from hashlib import md5
from common import config

def check_token_valid(token):
	if token and token in config.tokens:
		expire_time = config.tokens[token]['expire_time']
		if expire_time <= time.time():
			return False
		else:
			return True
	else:
		return False

def generate_task_id():
	task_id = '%d_%f' % (len(config.tasks), time.time())
	task_id = 'task_%s' % (md5(task_id.encode('utf-8')).hexdigest())
	return task_id

def save_task_data(task_id, task_data):
	task_path = 'task/%s' % task_id
	if not os.path.exists(task_path):
		os.mkdir(task_path)
	task_json = json.dumps(task_data)
	with open('%s/%s' % (task_path, 'data.json'), 'w') as f:
		f.write(task_json)
	return True
