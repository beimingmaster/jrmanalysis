#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: beimingmaster@gmail.com

from flask import Flask

app = Flask(__name__)

import handler.authorize
import handler.task
import handler.debug
