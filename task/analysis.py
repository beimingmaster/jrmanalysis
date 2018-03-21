#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: beimingmaster@gmail.com

import json
import requests
from optparse import OptionParser

def analysis(task_id):
	print('analysising')
	pass

if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-t', '--task', type='string', dest='task_id', help='task id to analysis')
	(options, args) = parser.parse_args()
	print('options: ', options)
	print('args: ', args)
	task_id = options.task_id
	if task_id:
		result = analysis(task_id)
	else:
		print('task id not provided')
	
