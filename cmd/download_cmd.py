#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: beimingmaster@gmail.com

import os
import time
import json
import requests
from optparse import OptionParser

def do_download(task_id):
	print('do download work for task id: %s ...' % task_id)
	file_url = None
	url_json_file = '../data/%s/url.json' % task_id
	data_json_file = '../data/%s/data.json' % task_id
	print('url json file: ', url_json_file)
	print('data json file: ', data_json_file)
	if not os.path.exists(url_json_file):
		print('url json file does not exist: ', url_json_file)
		return False
	elif os.path.exists(data_json_file):
		print('data json file does exist: ', data_json_file)
		return False
	with open(url_json_file, 'r', encoding='utf8') as f:
		url_json_data = json.load(f)
		if 'file_url' in url_json_data:
			file_url = url_json_data['file_url']
	print('file url: ', file_url)
	if file_url:
		try:
			r = requests.get(file_url, timeout=10)
			if r.status_code == 200:
				with open(data_json_file, 'w', encoding='utf8') as f:
					f.write(r.text)
			else:
				print('downloading task data has error: %s' % file_url)
		except Exception as ex:
			print('requests has error', ex)
	else:
		print('file url is no exists for task_id : %s' % task_id)
		return False

if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-t', '--task', type='string', dest='task_id', help='task id to analysis')
	(options, args) = parser.parse_args()
	print('options: ', options)
	print('args: ', args)
	task_id = options.task_id
	if task_id:
		start = time.time()
		do_download(task_id)
		end = time.time()
		print('doing download work takes %.2fs!' % (end-start))
	else:
		print('task id not provided')
	
