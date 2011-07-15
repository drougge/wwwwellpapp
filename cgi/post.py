#!/usr/bin/env python

from cgi import escape
import cgitb
import re
from os import environ
from sys import exit
from dbclient import dbclient, dbcfg

cgitb.enable()

outdata = []

def notfound():
	print "Status: 404 Not Found"
	print "Content-Type: text/html; charset=UTF-8"
	print
	print "404 Post not found"
	exit()

def prt(str):
	global outdata
	outdata.append(str)

def prtfields(*fields):
	map(lambda f: prt(f[0] + u'="' + escape(unicode(f[1])) + u'" '), fields)

m = environ["PATH_INFO"][1:]
if not re.match(r"^[0-9a-f]{32}$", m):
	notfound()

cfg = dbcfg(None, [".wellpapprc"])
client = dbclient(cfg)
post = client.get_post(m, wanted=["width", "height", "ext", "tagname", "tagguid"], separate_implied=True)
if not post: notfound()

def tagfmt(n):
	for s in u":_-/><&":
		n = n.replace(s, s + u'\u200b')
	return escape(n)
def taglist(post, impl):
	prefix = "impl" if impl else ""
	z = zip(post[prefix + "tagname"], post[prefix + "tagguid"])
	return [(tagfmt(n), g, impl) for n, g in z]
tags = sorted(taglist(post, False) + taglist(post, True))
rels = client.post_rels(m)
img = u'../image/' + m + u'.' + post["ext"]

def thumbs(posts):
	for m in posts:
		prt(u'<div>' + m + u'</div>')

prt(u"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>WWWwellpapp</title>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
	<link rel="stylesheet" href="../style.css" />
	<script src="../resize.js" type="text/javascript"></script>
</head>
<body>
""")
prt(u'<div id="main">\n')
prt(u'<div onclick="resize();" id="rescaled-msg">Image rescaled<br />click to see full size</div>\n')
prt(u'<img id="main-image" onclick="resize();" ')
prtfields((u'src', img), (u'alt', m), (u'width', post["width"]), (u'height', post["height"]))
prt(u'/>\n')
prt(u'<script type="text/javascript">resize();</script>\n')
if rels:
	prt(u'<div id="related">')
	prt(u'Related posts:')
	thumbs(rels)
	prt(u'</div>\n')
prt(u'</div>\n')
prt(u'<ul id="tags">')
for n, g, impl in tags:
	c = u'tag implied' if impl else u'tag'
	#c += u' tt-' + tt
	prt(u'<li class="' + c + u'"><a href="../tag/' + g + u'">'+ n + u'</a></li>\n')
prt(u'</ul>')
prt(u'</body></html>')

print "Content-Type: text/html; charset=UTF-8"
print
print u''.join(outdata).encode("utf-8")
