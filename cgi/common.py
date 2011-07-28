# -*- coding: utf-8 -*-

from cgi import escape, FieldStorage
import cgitb
from dbclient import dbclient, dbcfg
from urllib import urlencode
import re

cgitb.enable()

per_page = 32
outdata_head = []
outdata = []
client = dbclient(dbcfg(None, [".wellpapprc"]))
fs = FieldStorage(keep_blank_values=True)
user = "fake"
base = unicode(client.cfg.webbase)
assert base
thumbsize = unicode(client.cfg.thumb_sizes.split()[0])
assert thumbsize

def getarg(n, default=None, as_list=False):
	"""Get a (cgi) argument as a unicode string.
	Return the first occurance of the argument without as_list, and all
	occurances in a list with.
	If you don't pass a default you get an exception if the argument was
	not provided.
	"""
	if default is not None and n not in fs: return default
	a = fs[n]
	if isinstance(a, list):
		a = [_argdec(e.value) for e in a]
		if not as_list: a = u' '.join(a)
	else:
		a = _argdec(a.value)
		if as_list: a = a.split()
	return a
def _argdec(v):
	try:
		v = v.decode("utf-8")
	except Exception:
		v = v.decode("iso-8859-1")
	return v

def notfound():
	"""Return a 404 error"""
	print "Status: 404 Not Found"
	print "Content-Type: text/html; charset=UTF-8"
	print
	print "404 Not Found"
	exit()

def clean(n):
	"""Get tagname without prefix"""
	if n[0] in u"-~": return n[1:]
	return n
def prefix(n):
	"""Get prefix of tagname (if any)"""
	if n[0] in u"-~": return n[0]
	return ""

def prt(*a):
	"""Print (unicode) to client.
	Conceptually at least, nothing is actually sent until finish is called.
	"""
	outdata.extend(a)

def prtfields(*fields):
	"""Print (fieldname, value) pairs as html attributes
	Output ends with a space.
	"""
	map(lambda f: prt(f[0], u'="', escape(unicode(f[1])), u'" '), fields)

_zwsp_pre_re = re.compile(ur'([(<\[]|\b\d)')
_zwsp_post_re = re.compile(ur'([:/)>\]&\\,\._-])')
_zwsp_nr_re = re.compile(ur'(\d+)')
_zwsp_re = re.compile(ur'\u200b+')
def tagfmt(n, html_ok=True):
	"""Format a tagname for printing in html"""
	n = _zwsp_pre_re.sub(u'\u200b\\1', n)
	n = _zwsp_post_re.sub(u'\\1\u200b', n)
	n = _zwsp_nr_re.sub(u'\u200b\\1\u200b', n)
	n = _zwsp_re.sub(u'\u200b', n)
	return escape(n)

def tagname(guid):
	"""Tag guid -> name"""
	tag = client.get_tag(guid)
	return tag.name

def taglist(post, impl):
	"""Get a list of either implied or non-implied tags of a post.
	Returns (html formated name, tag, impl).
	"""
	if impl:
		full, weak = post.impltags, post.implweaktags
	else:
		full, weak = post.tags, post.weaktags
	full = [(tagfmt(t.name), t, impl) for t in full]
	weak = [(tagfmt(u'~' + t.name), t, impl) for t in weak]
	return full + weak

def tagcloud(guids):
	"""Get "tag cloud" for the search specified by guids
	Same return format as taglist, impl is always False.
	"""
	guids = set(guids)
	range = (0, 19 + len(guids))
	tags = client.find_tags("EI", "", range=range, guids=guids, order="-post")
	return [(tagfmt(t.name), t, False) for t in tags if t.guid not in guids]

def tagtypes():
	"""List of tag types."""
	return client.metalist("tagtypes")

def tag_post(p, full, weak, remove):
	"""Apply tag changes to a post"""
	post_full = set([t.guid for t in p.tags])
	post_weak = set([t.guid for t in p.weaktags])
	set_full = full.difference(post_full)
	set_weak = weak.difference(post_weak)
	set_remove_full = post_full.intersection(remove)
	set_remove_weak = post_weak.intersection(remove)
	set_remove = set_remove_full.union(set_remove_weak)
	if set_full or set_weak or set_remove:
		client.tag_post(p.md5, full_tags=set_full, weak_tags=set_weak, remove_tags=set_remove)
		return True

def prt_tags(tags):
	"""Print #tags list"""
	if not tags: return
	prt(u'<ul id="tags">')
	for n, t, impl in tags:
		c = u'tag implied' if impl else u'tag'
		prt(u'<li class="', c, u'"><a class="tt-', t.type, u'" href="',
		    base, u'tag/', t.guid, u'">', n, u'</a></li>\n')
	prt(u'</ul>')

def prt_posts(posts):
	"""Print #thumbs view"""
	prt(u'<div id="thumbs">\n')
	for post in posts:
		m = post.md5
		prt(u'<span class="thumb"')
		if user:
			prt(u' id="p', m, u'"')
		prt(u'><a href="', base, u'post/', m, u'"><img ')
		prtfields((u'src', base + u'image/' + thumbsize + u'/' + m), (u'alt', m))
		prtfields((u'title', tags_as_html(post)))
		prt(u'/></a></span>\n')
	prt(u'</div>\n')

def tags_as_html(post):
	"""Returns single string of HTML escaped tag names for post"""
	names = sorted([t.name for t in post.tags or []])
	names += sorted([u'~' + t.name for t in post.weaktags or []])
	return u' '.join([tagfmt(n, False) for n in names])

def prt_search_form(q=u''):
	"""Print search form"""
	prt(u'<form action="', base, u'search" method="get">\n',
	    u'<div id="search-box">\n',
	    u'<input type="text" name="q" id="search-q" value="', escape(q, True),
	    u'" onfocus="WP.comp_init(this);" />\n',
	    u'<input type="submit" value="Search" />\n',
	    u'</div>\n',
	    u'</form>\n')

def makelink(fn, *args):
	"""Make a html link to fn with (field, value) pairs as arguments"""
	fn = base + fn
	if not args: return fn
	if u'?' in fn:
		middle = u'&amp;'
	else:
		middle = u'?'
	args = urlencode([(a, v.encode("utf-8")) for a, v in args])
	return fn + middle + escape(args)

def pagelinks(link, page, result_count):
	"""Returns a string with the pagelinks suitable for this search
	link is the base-link, page is current page, result_count is number
	of results we can display (not pages).
	Also puts rel-links in <head>
	"""
	global outdata
	pages = range(result_count // per_page + 1)
	if len(pages) == 1:
		if not user: return u''
		pages = []
	real_outdata = outdata
	outdata = []
	if len(pages) > 16:
		if page < 8:
			pages = pages[:10] + pages[-6:]
		elif page > len(pages) - 8:
			pages = pages[:6] + pages[-10:]
		else:
			pages = pages[:6] + pages[page - 2:page + 3] + pages[-5:]
	prt(u'<div class="pagelinks">')
	prev = -1
	for p in pages:
		if p != prev + 1:
			prt(u'<span class="pagelink linkspace">...</span>\n')
		prev = p
		prt(u'<span class="pagelink')
		plink = link +  u'&amp;page=' + unicode(p)
		if p == page:
			prt(u' currentpage">')
		else:
			prt(u'"><a href="', plink, u'">')
		prt(unicode(p))
		if p != page:
			prt(u'</a>')
		prt(u'</span>\n')
		if p == 0:
			prt_rel(plink, "first")
		if p == page - 1:
			prt_rel(plink, "prev")
		elif p == page + 1:
			prt_rel(plink, "next")
	if pages: prt_rel(plink, "last")
	if user:
		if pages:
			prt(u'<span class="pagelink"><a href="', link,
			     '&amp;ALL=1">ALL</a></span>\n')
		prt(u'<span class="pagelink"><a href="' + base,
		    u'static/jserror.html" onclick="return WP.tm_init();">',
		    u'Tagmode</a></span>\n')
	prt(u'</div>\n')
	res = u''.join(outdata)
	outdata = real_outdata
	return res

def prt_tagform(m):
	"""Print form for tagging single image (m)"""
	prt(u'<form action="' + base + u'post-tag" method="post">\n',
	    u'<div id="tag-form">\n',
	    u'<input type="hidden" name="post" value="' + m + u'" />\n',
	    u'<input type="text" name="tags" id="tag-q" ',
	    u' onfocus="WP.comp_init(this);" />\n',
	    u'<input type="submit" value="Tag" />\n',
	    u'</div>\n',
	    u'</form>\n')

def prt_script(script, suffix=u'\n'):
	"""Print a script tag"""
	prt('<script src="', base, u'static/', script,
	    u'" type="text/javascript"></script>', suffix)

def prt_left_head():
	"""Print head of #left div"""
	prt(u'<div id="left">\n')

def prt_left_foot():
	"""Print foot of #left div"""
	prt(u'<div id="help"><a href="',
	    base, u'static/help.html',
	    u'">Help</a></div>\n',
	    u'</div>\n')

def prt_head(extra_script=None):
	"""Print page head
	Call before any other output"""
	global outdata
	outdata = outdata_head
	prt(u"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>WWWwellpapp</title>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
	<link rel="stylesheet" href="%(base)sstatic/style.css" />
	<link rel="stylesheet" href="%(base)sstatic/tagstyle.css" />
	<script src="%(base)sstatic/common.js" type="text/javascript"></script>
	<script type="text/javascript"><!--
		WP.uribase = "%(base)s";
	--></script>
	<link rel="help" href="%(base)sstatic/help.html" />""" % {"base": base})
	if extra_script:
		prt(u'\n\t')
		prt_script(extra_script, u'')
	outdata = []
	prt(u'\n</head>\n<body>\n')
	if user:
		prt(u'<div id="tagbar"></div>\n')

def prt_rel(href, rel):
	"""Add a rel link to head (if appropriate)"""
	if "ALL" in fs: return
	global outdata
	real_outdata = outdata
	outdata = outdata_head
	prt(u'\n\t<link rel="', rel, u'" href="', href, u'" />')
	outdata = real_outdata

def prt_foot():
	"""Print page foot"""
	prt_script(u'complete.js')
	if user: prt_script(u'tagmode.js')
	prt(u'</body></html>')

def finish(ctype = "text/html"):
	"""Finish up, actually sending page to client."""
	data = u''.join(outdata_head + outdata).encode("utf-8")
	ctype = str(ctype)
	if (ctype[:5] == "text/" or ctype == "application/json") and "charset" not in ctype:
		ctype += "; charset=UTF-8"
	print "Content-Type: " + ctype
	print "Content-Length: " + str(len(data) + 1)
	print
	print data
