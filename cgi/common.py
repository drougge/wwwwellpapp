# -*- coding: utf-8 -*-

from cgi import escape, FieldStorage
import cgitb
from dbclient import dbclient, dbcfg
from urllib import urlencode

cgitb.enable()

per_page = 32
outdata = []
client = dbclient(dbcfg(None, [".wellpapprc"]))
fs = FieldStorage(keep_blank_values=True)
user = "fake"
base = unicode(client.cfg.webbase)
assert base
thumbsize = unicode(client.cfg.thumb_sizes.split()[0])
assert thumbsize

def getarg(n, default=None, as_list=False):
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
	print "Status: 404 Not Found"
	print "Content-Type: text/html; charset=UTF-8"
	print
	print "404 Not Found"
	exit()

def clean(n):
	if n[0] in u"-~": return n[1:]
	return n
def prefix(n):
	if n[0] in u"-~": return n[0]
	return ""

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

def tagcloud(guids):
	guids = set(guids)
	posts = client.search_post(guids=guids, wanted=["tagname", "tagguid", "tagdata"])[0]
	tags = {}
	guid = {}
	for p in posts:
		for t in p.tags:
			tags[t.guid] = t
			guid[t.guid] = guid.get(t.guid, 0) + 1
	show = sorted(guid, lambda x, y: cmp(guid[y], guid[x]))
	show = [g for g in show[:20 + len(guids)] if g not in guids]
	return [(tagfmt(tags[g].name), tags[g], False) for g in show]

def tagtypes():
	# The server doesn't support this yet, so fake it for now
	return [u'unspecified', u'ambiguous', u'meta', u'inimage',
	        u'photographer', u'person', u'location', u'text', u'group']

def tag_post(p, full, weak, remove):
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
	if not tags: return
	prt(u'<ul id="tags">')
	for n, t, impl in tags:
		c = u'tag implied' if impl else u'tag'
		prt(u'<li class="' + c + u'"><a class="tt-' + t.type + u'" href="')
		prt(base + u'tag/' + t.guid + u'">'+ n + u'</a></li>\n')
	prt(u'</ul>')

def prt_posts(posts):
	prt(u'<div id="thumbs">\n')
	for post in posts:
		m = post.md5
		prt(u'<span class="thumb"')
		if user:
			prt(u' id="p' + m + u'"')
		prt(u'><a href="' + base + u'post/' + m + u'"><img ')
		prtfields((u'src', base + u'image/' + thumbsize + u'/' + m), (u'alt', m))
		prtfields((u'title', tags_as_html(post)))
		prt(u'/></a></span>\n')
	prt(u'</div>\n')

def tags_as_html(post):
	names = sorted([t.name for t in post.tags or []])
	names += sorted([u'~' + t.name for t in post.weaktags or []])
	return u' '.join([tagfmt(n, False) for n in names])

def prt_search_form(q=u''):
	prt(u'<form action="' + base + u'search" method="get">\n')
	prt(u'<div id="search-box">\n')
	prt(u'<input type="text" name="q" id="search-q" value="' + escape(q, True))
	prt(u'" onfocus="WP.comp_init(this);" />\n')
	prt(u'<input type="submit" value="Search" />\n')
	prt(u'</div>\n')
	prt(u'</form>\n')

def makelink(fn, *args):
	fn = base + fn
	if not args: return fn
	if u'?' in fn:
		middle = u'&amp;'
	else:
		middle = u'?'
	args = urlencode([(a, v.encode("utf-8")) for a, v in args])
	return fn + middle + escape(args)

def pagelinks(link, page, result_count):
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
		if p == page:
			prt(u' currentpage">')
		else:
			prt(u'"><a href="' + link)
			prt(u'&amp;page=' + unicode(p) + u'">')
		prt(unicode(p))
		if p != page:
			prt(u'</a>')
		prt(u'</span>\n')
	if user:
		if pages:
			prt(u'<span class="pagelink"><a href="' + link)
			prt(u'&amp;ALL=1">ALL</a></span>\n')
		prt(u'<span class="pagelink"><a href="' + base);
		prt(u'static/jserror.html" onclick="return WP.tm_init();">')
		prt(u'Tagmode</a></span>\n')
	prt(u'</div>\n')
	res = u''.join(outdata)
	outdata = real_outdata
	return res

def prt_tagform(m):
	prt(u'<form action="' + base + u'post-tag" method="post">\n')
	prt(u'<div id="tag-form">\n')
	prt(u'<input type="hidden" name="post" value="' + m + u'" />\n')
	prt(u'<input type="text" name="tags" id="tag-q" ');
	prt(u' onfocus="WP.comp_init(this);" />\n')
	prt(u'<input type="submit" value="Tag" />\n')
	prt(u'</div>\n')
	prt(u'</form>\n')

def prt_script(script, suffix=u'\n'):
	prt('<script src="' + base + u'static/' + script)
	prt(u'" type="text/javascript"></script>' + suffix)

def prt_head(extra_script=None):
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
	--></script>""" % {"base": base})
	if extra_script:
		prt(u'\n\t')
		prt_script(extra_script, u'');
	prt(u'\n</head>\n<body>\n')
	if user:
		prt(u'<div id="tagbar"></div>\n')

def prt_foot():
	prt_script(u'complete.js')
	if user: prt_script(u'tagmode.js')
	prt(u'</body></html>')

def finish(ctype = "text/html"):
	data = u''.join(outdata).encode("utf-8")
	ctype = str(ctype)
	if (ctype[:5] == "text/" or ctype == "application/json") and "charset" not in ctype:
		ctype += "; charset=UTF-8"
	print "Content-Type: " + ctype
	print "Content-Length: " + str(len(data) + 1)
	print
	print data
