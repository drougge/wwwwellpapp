#!/usr/bin/env python

from os.path import exists
from os import stat
from time import strftime, gmtime, time

from bottle import route, abort, response
from common import init

def fmttime(t):
	return strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime(t))

def serve(fn, ext):
	if not exists(fn):
		abort(404)
	z = stat(fn).st_size
	print fn,z
	response.content_type = "image/" + ext
	response.set_header("Content-Lenght", str(z))
	response.set_header("Expires", fmttime(time() + 60*60*24 * 10))
	response.set_header("Date", fmttime(time()))
	return open(fn, "rb")

@route("/image/<z>/<m:re:[0-9a-z]{32}>")
def thumb(m, z):
	client = init()
	if z in ("normal", "large"):
		return serve(client.pngthumb_path(m, z), "png")
	else:
		return serve(client.thumb_path(m, z), "jpeg")

@route("/image/<m:re:[0-9a-z]{32}>.<ext:re:[a-z]{3,4}>")
def image(m, ext):
	client = init()
	return serve(client.image_path(m), ext)
