# -*- coding: utf-8 -*-

from os.path import exists
from os import stat
from time import strftime, gmtime, time

from bottle import get, abort, response
from wellpapp import RawWrapper, raw_exts

def fmttime(t):
	return strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime(t))

def serve(fn, ext):
	if not exists(fn):
		abort(404)
	if ext in raw_exts:
		fh = RawWrapper(open(fn, "rb"), True)
		fh.seek(0, 2)
		z = fh.tell()
		fh.seek(0)
		ext = "jpeg"
	else:
		z = stat(fn).st_size
		fh = open(fn, "rb")
	response.content_type = "image/" + ext
	response.set_header("Content-Length", str(z))
	response.set_header("Expires", fmttime(time() + 60*60*24 * 10))
	response.set_header("Date", fmttime(time()))
	return fh

@get("/image/<z>/<m:re:[0-9a-z]{32}>")
def thumb(m, z, client):
	if z in ("normal", "large"):
		return serve(client.pngthumb_path(m, z), "png")
	else:
		return serve(client.thumb_path(m, z), "jpeg")

@get("/image/<m:re:[0-9a-z]{32}>.<ext:re:[a-z]{3,4}>")
def r_image(m, ext, client):
	return serve(client.image_path(m), ext)
