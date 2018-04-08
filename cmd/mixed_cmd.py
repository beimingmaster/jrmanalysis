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

import download_cmd
import analysis_cmd

from common import config

def do_mixed(task_id):
    print('do mixed work for task id: %s ...' % task_id)
    start = time.time()
    download_cmd.do_download(task_id)
    end = time.time()
    print('do download takes %.2fs' % (end-start))
    start = end
    analysis_cmd.do_analysis(task_id)
    end = time.time()
    print('do analysis takes %.2fs' % (end-start))

def get_wait_task():
    wait_url = '%s/v1/api/task/wait?token=%s' % (config.api_url, config.admin_token)
    print('task wait url: ', wait_url)
    try:
        r = requests.get(wait_url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception as ex:
        print('get wait task has error: %s' % ex)
        return None

def change_task_status(task_id, task_status):
    change_url = '%s/v1/api/task/status?token=%s' % (config.api_url, config.admin_token)
    print('task status change url: ', change_url)
    result_json_file = '../data/%s/result.json' % task_id
    if os.path.exists(result_json_file):
        try:
            data = {'task_id': task_id, 'task_status': task_status}
            r = requests.post(change_url, json=data)
            if r.status_code == 200:
                return True
        except Exception as ex:
            print('change task status has error: %s' % ex)
            return False    

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-t', '--task', type='string', dest='task_id', help='task id to analysis')
    (options, args) = parser.parse_args()
    print('options: ', options)
    print('args: ', args)
    task_id = options.task_id
    wait_task = False
    if task_id == 'wait':
        wait_task = True
        task_id = None
        print('get wait task ...')
        task = get_wait_task()
        if task and 'task_id' in task:
            task_id = task['task_id']
            print('wait task got, task id: %s' % task_id)
        else:
            print('no wait task')
    if task_id:
        start = time.time()
        do_mixed(task_id)
        if wait_task:
            change_task_status(task_id, 1)
        end = time.time()
        print('do mixed work takes %.2fs!' % (end-start))
    else:
        print('task id not provided')
    
