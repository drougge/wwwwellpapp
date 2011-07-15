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
	print "404 Not Found"
	exit()

def prt(str):
	outdata.append(str)

def prtfields(*fields):
	map(lambda f: prt(f[0] + u'="' + escape(unicode(f[1])) + u'" '), fields)

def tagfmt(n):
	for s in u":_-/><&":
		n = n.replace(s, s + u'\u200b')
	return escape(n)

def tagname(guid):
	tag = client.get_tag(guid)
	return tag["name"]

def taglist(post, impl):
	prefix = "impl" if impl else ""
	z = zip(post[prefix + "tagname"], post[prefix + "tagguid"])
	return [(tagfmt(n), g, impl) for n, g in z]

def prt_tagbox(tags):
	prt(u'<ul id="tags">')
	for n, g, impl in sorted(tags):
		c = u'tag implied' if impl else u'tag'
		#c += u' tt-' + tt
		prt(u'<li class="' + c + u'"><a href="../tag/' + g + u'">'+ n + u'</a></li>\n')
	prt(u'</ul>')

def prt_posts(posts):
	prt(u'<div id="thumbs">\n')
	for post in posts:
		m = post["md5"]
		prt('<div class="thumb"><a href="../post/' + m + u'"><img ')
		prtfields((u'src', u'../image/200/' + m), (u'alt', m))
		if "tagname" in post:
			title = u' '.join([tagfmt(n) for n in sorted(post["tagname"])])
			prtfields((u'title', title))
		prt(u'></a></div>')
	prt(u'</div>')

def prt_head(extra=u''):
	prt(u"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>WWWwellpapp</title>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
	<link rel="stylesheet" href="../style.css" />
	""")
	prt(extra)
	prt(u'</head>\n<body>\n')

def prt_foot():
	prt(u'</body></html>')

def finish():
	print "Content-Type: text/html; charset=UTF-8"
	print
	print u''.join(outdata).encode("utf-8")
