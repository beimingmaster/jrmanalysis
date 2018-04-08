#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: beimingmaster@gmail.com

import os
import sys
import time
import json
import requests
from optparse import OptionParser

sys.path.append('..')

from task import analysis

def do_analysis(task_id):
    print('do analysis work for task id: %s ...' % task_id)
    data_json_file = '../data/%s/data.json' % task_id
    print('data json file: ', data_json_file)
    if not os.path.exists(data_json_file):
        print('data json file does not exist: ', data_json_file)
        return False
    analy = analysis.CarRecordAnalysis(task_id)
    analy.doWork()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-t', '--task', type='string', dest='task_id', help='task id to analysis')
    (options, args) = parser.parse_args()
    print('options: ', options)
    print('args: ', args)
    task_id = options.task_id
    if task_id:
        start = time.time()
        do_analysis(task_id)
        end = time.time()
        print('doing analysis work takes %.2fs!' % (end-start))
    else:
        print('task id not provided')
    
