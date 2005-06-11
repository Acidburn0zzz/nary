#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, string, re, shutil, pisiconfig
from shell import *

def gnuconfig_findnewest():
	''' find the newest config.* file according to timestamp and return it '''

	locations = [ '/usr/share/gnuconfig/config.sub', '/usr/share/automake-1.8/config.sub', '/usr/share/automake-1.7/config.sub', '/usr/share/automake-1.6/config.sub', '/usr/share/automake-1.5/config.sub', '/usr/share/automake-1.4/config.sub' ]
	
	newer_location = {}

	for i in locations:
		newer_location[i] = re.sub( '\'', '', string.split( ( cat( i ) | tr( str.rstrip ) | grep ( '^timestamp' ) | join ), '=')[1] )

	keys = newer_location.keys()
	keys.sort()
	map(newer_location.get, keys )

	return os.path.dirname( newer_location.popitem()[0] )

def gnuconfig_update():
	''' copy newest config.* onto source's '''

	newer_location = gnuconfig_findnewest()

	try:
		shutil.copyfile( newer_location + '/config.sub', os.getcwd() + '/config.sub' )
		shutil.copyfile( newer_location + '/config.guess', os.getcwd() + '/config.guess' )
	except IOError:
		print 'Hata mata...'
		sys.exit()

	print 'GNU Config Update Finished...'
