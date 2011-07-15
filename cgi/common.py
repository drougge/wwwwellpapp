# -*- coding: utf-8 -*-

from cgi import escape
import cgitb
from dbclient import dbclient, dbcfg

cgitb.enable()

outdata = []
client = dbclient(dbcfg(None, [".wellpapprc"]))

def notfound():
	print "Status: 404 Not Found"
	print "Content-Type: text/html; charset=UTF-8"
	print
	print "404 Post not found"
	exit()

def prt(str):
	outdata.append(str)

def prtfields(*fields):
	map(lambda f: prt(f[0] + u'="' + escape(unicode(f[1])) + u'" '), fields)

def tagfmt(n):
	for s in u":_-/><&":
		n = n.replace(s, s + u'\u200b')
	return escape(n)

def taglist(post, impl):
	prefix = "impl" if impl else ""
	z = zip(post[prefix + "tagname"], post[prefix + "tagguid"])
	return [(tagfmt(n), g, impl) for n, g in z]

def thumbs(posts):
	for m in posts:
		prt(u'<div>' + m + u'</div>')

def prt_tagbox(tags):
	prt(u'<ul id="tags">')
	for n, g, impl in sorted(tags):
		c = u'tag implied' if impl else u'tag'
		#c += u' tt-' + tt
		prt(u'<li class="' + c + u'"><a href="../tag/' + g + u'">'+ n + u'</a></li>\n')
	prt(u'</ul>')

def finish():
	print "Content-Type: text/html; charset=UTF-8"
	print
	print u''.join(outdata).encode("utf-8")
