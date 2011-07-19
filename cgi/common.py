# -*- coding: utf-8 -*-

from cgi import escape, FieldStorage
import cgitb
from dbclient import dbclient, dbcfg
from urllib import urlencode

cgitb.enable()

per_page = 32
outdata = []
client = dbclient(dbcfg(None, [".wellpapprc"]))
fs = FieldStorage()
user = "fake"

def getarg(n):
	v = fs[n].value
	try:
		v = v.decode("utf-8")
	except Exception:
		v = v.decode("iso-8859-1")
	return v

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

def tagfmt(n, html_ok=True):
	for s in u":_-/><&":
		n = n.replace(s, s + u'\u200b')
	n = escape(n)
	if html_ok: n = n.replace(u'\u200b', u'<span class="wbr">\u200b</span>')
	return n

def tagname(guid):
	tag = client.get_tag(guid)
	return tag.name

def taglist(post, impl):
	if impl:
		full, weak = post.impltags, post.implweaktags
	else:
		full, weak = post.tags, post.weaktags
	full = [(tagfmt(t.name), t, impl) for t in full]
	weak = [(tagfmt(u'~' + t.name), t, impl) for t in weak]
	return full + weak

def prt_tags(tags):
	prt(u'<ul id="tags">')
	for n, t, impl in sorted(tags):
		c = u'tag implied' if impl else u'tag'
		c += u' tt-' + t.type
		prt(u'<li class="' + c + u'"><a href="../tag/' + t.guid + u'">'+ n + u'</a></li>\n')
	prt(u'</ul>')

def prt_posts(posts):
	prt(u'<div id="thumbs">\n')
	for post in posts:
		m = post.md5
		prt('<span class="thumb"><a href="../post/' + m + u'"><img ')
		prtfields((u'src', u'../image/200/' + m), (u'alt', m))
		if "tagname" in post:
			title = u' '.join([tagfmt(n, False) for n in sorted(post.tagname)])
			prtfields((u'title', title))
		prt(u'/></a></span>\n')
	prt(u'</div>\n')

def prt_search_form(q=u''):
	prt(u'<form action="../search/" method="get">\n')
	prt(u'<div id="search-box">\n')
	prt(u'<input type="text" name="q" value="' + escape(q, True) + u'" />\n')
	prt(u'<input type="submit" name="sBtn" value="Search" />\n')
	prt(u'</div>\n')
	prt(u'</form>\n')

def makelink(base, *args):
	if not args: return base
	if u'?' in base:
		middle = u'&amp;'
	else:
		middle = u'?'
	args = urlencode([(a, v.encode("utf-8")) for a, v in args])
	return base + middle + escape(args)

def pagelinks(link, page, result_count):
	global outdata
	pages = range(result_count // per_page + 1)
	if len(pages) == 1: return u''
	real_outdata = outdata
	outdata = []
	if len(pages) > 16:
		if page < 8:
			pages = pages[:10] + pages[-6:]
		elif page > len(pages) - 8:
			pages = pages[:6] + pages[-10:]
		else:
			pages = pages[:6] + pages[page - 2:page + 3] + pages[-5:]
	prt(u'<div>')
	prev = -1
	for p in pages:
		if p != prev + 1:
			prt(u'<div class="pagelink linkspace">...</div>\n')
		prev = p
		prt(u'<div class="pagelink')
		if p == page:
			prt(u' currentpage">')
		else:
			prt(u'"><a href="' + link)
			prt(u'&amp;page=' + unicode(p) + u'">')
		prt(unicode(p))
		if p != page:
			prt(u'</a>')
		prt(u'</div>\n')
	if user and page >= 0:
		prt(u'<div class="pagelink"><a href="' + link + u'&amp;ALL=1">ALL</a></div>\n')
	prt(u'</div>')
	res = u''.join(outdata)
	outdata = real_outdata
	return res

def prt_head(extra=u''):
	prt(u"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>WWWwellpapp</title>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
	<link rel="stylesheet" href="../style.css" />
	<link rel="stylesheet" href="../tagstyle.css" />
	""")
	prt(extra)
	prt(u'</head>\n<body>\n')

def prt_foot():
	prt(u'</body></html>')

def finish():
	data = u''.join(outdata).encode("utf-8")
	print "Content-Type: text/html; charset=UTF-8"
	print "Content-Length: " + str(len(data) + 1)
	print
	print data
