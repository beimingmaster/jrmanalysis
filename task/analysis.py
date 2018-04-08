#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: beimingmaster@gmail.com

import time
import json
import requests
import numpy as np
import pandas as pd

from geopy.distance import vincenty
from optparse import OptionParser

class CarRecordAnalysis(object):
    def __init__(self, task_id):
        self.task_id = task_id
        self.car_records = []
        self.car_road_paths = []
        self.car_road_path_clusters = []

    def doWork(self):
        self.doPrepare()
        self.doClean()
        self.doAnalysis()
        self.doFinish()
    
    def doPrepare(self):
        print('do prepare data ...')
        task_data_file = '../data/%s/data.json' % self.task_id
        with open(task_data_file, 'r') as f:
            data = json.load(f)
            if data:
                if 'car_records' in data:
                    self.raw_car_records = data['car_records']
                else:
                    self.raw_car_records = data
                return True
            else:
                self.raw_car_records = []
                return False
    
    def doClean(self):
        print('do clean data ...')  
        car_records = []
        for record in self.raw_car_records:
            record_adjust = {'device_id': record['device_id'], 'device_car_id': record['device_car_id'], 
                'device_lat': record['device_latlng']['coordinates'][1], 
                'device_lng': record['device_latlng']['coordinates'][0], 
                'device_loctime': record['device_loctime'], 'device_address': record['device_address'], 
                'device_speed': record['device_speed'], 'device_loctype': record['device_loctype']}
            car_records.append(record_adjust)
        columns = ['device_id', 'device_car_id', 'device_lat', 'device_lng', 
            'device_address', 'device_loctime', 'device_loctimestamp', 'device_speed', 'device_loctype']
        pd_car_records = pd.DataFrame(car_records, columns=columns)
        pd_car_records['device_loctimestamp'] = pd_car_records['device_loctime']
        pd_car_records['device_loctime'] = pd.to_datetime(pd_car_records['device_loctime'], unit='s')
        print('shape of pd car records: ', pd_car_records.shape)
        selected_cols = pd_car_records.columns[2:8]
        pd_car_records = pd_car_records[selected_cols]
        pd_car_records = pd_car_records.sort_values(by=['device_loctime'])
        pd_car_records = pd_car_records.dropna()
        pd_car_records.reset_index(drop=True)
        self.pd_car_records = pd_car_records
        self.pd_car_matrix = self.pd_car_records.as_matrix()
        print('shape of pd car matrix: ', self.pd_car_matrix.shape)
        
    def doAnalysis(self):
        print('do analysis ...')
        self.doAnalysisForTimeDiff()
        self.doAnalysisForRoadPaths()
        self.doAnalysisForRoadPathClusters()

    def doAnalysisForTimeDiff(self):
        time_diff = self.pd_car_records['device_loctimestamp'].diff()
        time_diff = time_diff / 3600.0
        self.time_diff = time_diff

    def doAnalysisForRoadPaths(self):
        print('do analysis for road paths ...')
        
        car_road_paths = []

        start_point = None
        end_point = None
        distance = 0.0

        speed_threshold = 10.0
        time_threshold = 0.16
        distance_threshold = 1.0

        time_idx = 4
        speed_idx = 5

        road_amount = self.pd_car_matrix.shape[0]

        for i in range(0, road_amount):
            if start_point is None and self.pd_car_matrix[i][speed_idx] > speed_threshold:
                start_point = self.pd_car_matrix[i]
                end_point = self.pd_car_matrix[i]
                distance = 0.0
            if self.time_diff[i] > time_threshold: #time diff > 10mins, think it's a stop
                if start_point is not None and end_point is not None:
                    time_gap = end_point[time_idx] - start_point[time_idx]
                    distance_gap = self.calcDistance(start_point, end_point) #direct distance
                    car_road_paths.append([start_point, end_point, time_gap, distance, distance_gap])
                    start_point = None
                    end_point = None
                    distance = 0.0
                    if self.pd_car_matrix[i][speed_idx] > speed_threshold:
                        start_point = self.pd_car_matrix[i]
                        end_point = self.pd_car_matrix[i]
            else:
                if self.pd_car_matrix[i][speed_idx] > speed_threshold:
                    distance += self.calcDistance(end_point, self.pd_car_matrix[i])
                    end_point = self.pd_car_matrix[i]
        
        print('count of road paths: ', len(car_road_paths))
        
        #remove invalid road path
        road_time_idx = 2
        road_distance_idx = 3
        road_direct_distance_idx = 4

        car_road_valids = [False]*len(car_road_paths)
        for i, road_path in enumerate(car_road_paths):
            road_time_gap = road_path[road_time_idx] / 3600.0 
            road_distance_gap = road_path[road_distance_idx] / 1000.0
            road_direct_distance_gap = road_path[road_direct_distance_idx] / 1000.0
            avg_speed = road_distance_gap / (road_time_gap + 0.00001)
            if road_time_gap > time_threshold and road_distance_gap > distance_threshold and road_direct_distance_gap > distance_threshold and avg_speed > speed_threshold:
                car_road_valids[i] = True

        count = len(car_road_paths)
        for i in range(count):
            if not car_road_valids[count-1-i]:
                del car_road_paths[count-1-i]

        print('count of road paths after removing invalid: ', len(car_road_paths))

        self.car_road_paths = car_road_paths

    def doAnalysisForRoadPathClusters(self):
        print('do analysis for road path clusters ...')
        self.car_road_path_clusters = []
        count = len(self.car_road_paths)
        for i in range(0, count-1):
            for j in range(i+1, count):
                r1 = self.car_road_paths[i]
                r2 = self.car_road_paths[j]
                if self.isSimilarRoadPath(r1, r2):
                    road_path_cluster = self.getRoadPathCluster(i)
                    if road_path_cluster:
                        road_path_cluster.add(j)
                    else:
                        self.car_road_path_clusters.append(set([i, j]))

        self.car_road_path_clusters = sorted(self.car_road_path_clusters, key=len, reverse=True)

        print('count of road path clusters: ', len(self.car_road_path_clusters))

    def doFinish(self):
        print('do finish for task: %s' % self.task_id)
        task_result_file = '../data/%s/result.json' % self.task_id       
        with open(task_result_file, 'w') as f:
            for i, road_path_cluster in enumerate(self.car_road_path_clusters):
                f.write('%s\r\n' % (sorted(road_path_cluster)))

    def calcDistance(self, p1, p2):
        v1 = (p1[0], p1[1])
        v2 = (p2[0], p2[1])
        return (vincenty(v1, v2).m)

    def isSimilarRoadPath(self, r1, r2):
        d1 = self.calcDistance(r1[0], r2[0])
        d2 = self.calcDistance(r1[1], r2[1])
        if d1 < 1000.0 and d2 < 1000.0:
            return True
        else:
            return False

    def getRoadPathCluster(self, road_path_idx):
        for i, road_path_cluster in enumerate(self.car_road_path_clusters):
            if road_path_idx in road_path_cluster:
                return road_path_cluster

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-t', '--task', type='string', dest='task_id', help='task id to analysis')
    (options, args) = parser.parse_args()
    print('options: ', options)
    print('args: ', args)
    task_id = 'task_011ecd6d30c69ca5cd0c1434cbe6604b'
    if task_id:
        analysis = CarRecordAnalysis(task_id)
        start = time.time() 
        analysis.doWork()
        end = time.time()
        print('analysising takes %.2fs!' % (end-start))
    else:
        print('task id not provided')
    
