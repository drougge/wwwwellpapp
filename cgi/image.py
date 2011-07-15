#!/usr/bin/env python

import cgitb
import re
from os import environ
from sys import exit
from dbclient import dbclient, dbcfg
from os.path import exists
from os import stat
from sys import stdout

cgitb.enable()

def notfound():
	print "Status: 404 Not Found"
	print "Content-Type: text/html; charset=UTF-8"
	print
	print "404 Post not found"
	exit()

def serve(fn, ext):
	if not exists(fn): notfound()
	z = stat(fn).st_size
	print "Content-Type: image/" + ext
	print "Content-Lenght: " + str(z)
	print
	fh = open(fn)
	data = fh.read(65536)
	while data:
		stdout.write(data)
		data = fh.read(65536)

def check_m(m):
	if not re.match(r"^[0-9a-f]{32}$", m):
		notfound()

cfg = dbcfg(None, [".wellpapprc"])
client = dbclient(cfg)

args = environ["PATH_INFO"][1:]
if "." in args: # this is a full size image
	args = args.split(".")
	if len(args) != 2: notfound()
	m, t = args
	check_m(m)
	serve(client.image_path(m), t)
elif "/" in args: # this is a thumb
	args = args.split("/")
	if len(args) != 2: notfound()
	z, m = args
	check_m(m)
	if z in ("normal", "large"):
		serve(client.pngthumb_path(m, z), "png")
	else:
		serve(client.thumb_path(m, z), "jpeg")
else:
	notfound()
