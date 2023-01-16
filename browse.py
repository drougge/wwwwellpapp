# -*- coding: utf-8 -*-

from os import listdir, stat
from os.path import normpath, exists, join as joinpath, isfile, isdir
from hashlib import md5

import common
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
	if not common.cfg.browsebase:
		abort(403)
	# Three slashes, because normpath is stupidly posix-compliant.
	pathpart = normpath("///" + path)
	path = normpath(common.cfg.browsebase + pathpart)
	if not exists(path):
		abort(403)
	client = common.init()
	
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
	
	common.prt_head()
	common.prt_left_head()
	common.prt('<ul id="dirs">\n')
	for d in dirs:
		common.prt('<li><a href="', d, '/">', d, '</a></li>\n')
	common.prt('</ul>\n')
	common.prt_left_foot()
	common.prt('<div id="main">\n',
	    '<h1>', pathpart, '</h1>\n',
	    common.pagelinks('', 0, 0))
	common.prt_posts([p[1] for p in sorted(posts)])
	common.prt('</div>\n')
	common.prt_foot()
	return common.finish()
