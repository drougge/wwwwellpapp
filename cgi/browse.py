#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import environ, listdir, stat
from sys import exit
from common import *
from os.path import normpath, exists, join as joinpath, isfile, isdir
from hashlib import md5

def forbidden():
	global outdata
	print "Status: 403 Forbidden"
	outdata = []
	prt_head()
	prt(u'<h1>Forbidden</h1>\n')
	prt(u'<p>You are not allowed to access this directory.</p>\n')
	prt_foot()
	finish()
	exit(0)

def md5file(fn):
	m = md5()
	with file(fn, "rb") as fh:
		for data in iter(lambda: fh.read(65536), ""):
			m.update(data)
	return m.hexdigest()

if not client.cfg.browsebase: forbidden()
# Three slashes, because normpath is stupidly posix-compliant.
pathpart = normpath("///" + environ["PATH_INFO"])
path = normpath(client.cfg.browsebase + pathpart)
if not exists(path): forbidden()

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
prt(u'<div id="left">\n')
prt(u'<ul id="dirs">\n')
for d in dirs:
	prt(u'<li><a href="' + d + u'/">' + d + u'</a></li>\n')
prt(u'</ul>\n')
prt(u'</div>\n')
prt(u'<div id="main">\n')
prt(u'<h1>' + pathpart + u'</h1>\n')
prt_posts([p[1] for p in sorted(posts)])
prt(u'</div>\n')
prt_foot()
finish()
