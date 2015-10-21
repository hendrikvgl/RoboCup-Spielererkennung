#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

def record(duration,device): 
	if not os.path.exists('~/audio'):
		os.system("mkdir ~/audio")
	os.system("arecord -v --device=%s --use-strftime ~/audio/%%H-%%M-%%v.wav" % (device) )

if (len(sys.argv) < 2):
	duration = 60
else:
	try:
		duration = int(sys.argv[1])
	except ValueError:
		duration = 60

if (len(sys.argv) < 3):
	device = "default:CARD=U0x46d0x80a"
else:
	device = sys.argv[2]

record(duration,device)

