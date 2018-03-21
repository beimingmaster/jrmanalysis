#!/usr/bin/python
 # -*- coding: utf-8 -*-

#author: beimingmaster@gmail.com

from flask import Flask
from handler import app

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
