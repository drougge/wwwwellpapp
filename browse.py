# -*- coding: utf-8 -*-

from os import listdir, stat
from os.path import normpath, exists, join as joinpath, isfile, isdir
from hashlib import md5

from common import *
from bottle import get, abort

def md5file(fn):
	m = md5()
	with open(fn, 'rb') as fh:
		for data in iter(lambda: fh.read(65536), b''):
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
	prt('<ul id="dirs">\n')
	for d in dirs:
		prt('<li><a href="', d, '/">', d, '</a></li>\n')
	prt('</ul>\n')
	prt_left_foot()
	prt('<div id="main">\n',
	    '<h1>', pathpart, '</h1>\n',
	    pagelinks('', 0, 0))
	prt_posts([p[1] for p in sorted(posts)])
	prt('</div>\n')
	prt_foot()
	return finish()
