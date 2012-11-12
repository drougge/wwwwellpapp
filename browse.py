#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import listdir, stat
from os.path import normpath, exists, join as joinpath, isfile, isdir
from hashlib import md5

from common import *
from bottle import get, abort

def md5file(fn):
	m = md5()
	with file(fn, "rb") as fh:
		for data in iter(lambda: fh.read(65536), ""):
			m.update(data)
	return m.hexdigest()

@get("/browse/")
@get("/browse/<path:path>")
def r_browse(path=""):
	if not cfg.browsebase:
		abort(403)
	# Three slashes, because normpath is stupidly posix-compliant.
	pathpart = normpath("///" + path)
	path = normpath(cfg.browsebase + pathpart)
	if not exists(path):
		abort(403)
	client = init()
	
	posts = []
	dirs = []
	for fn in listdir(path):
		ffn = joinpath(path, fn)
		if isfile(ffn):
			m = md5file(ffn)
			p = client.get_post(m)
			if p:
				t = stat(ffn).st_mtime
				posts.append((t, p))
		elif isdir(ffn):
			dirs.append(fn)
	dirs.sort()
	if pathpart != "/": dirs = [".."] + dirs
	
	prt_head()
	prt_left_head()
	prt(u'<ul id="dirs">\n')
	for d in dirs:
		prt(u'<li><a href="', d, u'/">', d, u'</a></li>\n')
	prt(u'</ul>\n')
	prt_left_foot()
	prt(u'<div id="main">\n',
	    u'<h1>', pathpart, u'</h1>\n',
	    pagelinks(u'', 0, 0))
	prt_posts([p[1] for p in sorted(posts)])
	prt(u'</div>\n')
	prt_foot()
	return finish()
