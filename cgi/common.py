# -*- coding: utf-8 -*-

from cgi import escape, FieldStorage
import cgitb
from wellpapp import Client, Config
from urllib import urlencode
import re
from math import ceil

cgitb.enable()

per_page = 32
outdata_head = []
outdata = []
client = Client(Config(local_rc=True))
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
	print "Content-Type: text/plain; charset=UTF-8"
	print
	print "404 Not Found"
	exit()

def tag_clean(n):
	"""Get tagname without prefix"""
	if n[0] in u"-~!": return n[1:]
	return n
def tag_prefix(n):
	"""Get prefix of tagname (if any)"""
	if n[0] in u"-~!": return n[0]
	return u''

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
	pre = tag_prefix(guid)
	tag = client.get_tag(tag_clean(guid))
	return pre + tag.name

def taglist(post, impl):
	"""Get a list of either implied or non-implied tags of a post.
	Returns (html formated name, tag, impl).
	"""
	if impl:
		l = post.impltags
	else:
		l = post.settags
	return [(tagfmt(t.pname), t, impl) for t in l]

def tagcloud(guids):
	"""Get "tag cloud" for the search specified by guids
	Same return format as taglist, impl is always False.
	"""
	guids = set(guids)
	range = (0, 19 + len(guids))
	tags = client.find_tags("EI", "", range=range, guids=guids, order="-post", flags="-datatag")
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

def prt_tags(tags, q=None):
	"""Print #tags list"""
	if not tags: return
	prt(u'<ul id="tags">')
	for n, t, impl in tags:
		c = u'tag implied' if impl else u'tag'
		if t.ordered: c += u' ordered'
		prt(u'<li class="', c, u'"><a class="tt-', t.type, u'" href="',
		    base, u'tag/', t.guid, u'">', n, u'</a>')
		if q:
			prt(u'\n<ul>')
			for prefix, caption in (u' ', u'+'), (u' -', u'-'):
				qa = prefix + t.name
				link = makelink(u'search', (u'q', q + qa))
				prt(u'<li><a href="', link, u'">', caption, u'</a></li>')
			prt(u'</ul>\n')
		prt(u'</li>\n')
	prt(u'</ul>')

def prt_qs(names, tags, tagaround=None):
	"""Print #query-string list"""
	def prt_mod(q, tags, caption):
		q = u' '.join([q for q, t in zip(q, tags) if t])
		link = makelink(u'search', (u'q', q))
		prt(u'<li><a href="', link, u'">', caption, u'</a></li>')
	prt(u'<ul id="query-string">\n')
	for name, tag, i in zip(names, tags, range(len(tags))):
		if not tag:
			prt(u' <li class="unknown">', tagfmt(name), u'</li>\n')
			continue
		c = u' class="tt-' + tag.type + u'"'
		prefix = tag_prefix(name)
		clean = tag_clean(name)
		if tagaround:
			prt(u' <li><', tagaround, c, u'>', tagfmt(name), u'</', tagaround, u'>')
		else:
			prt(u' <li>', prefix, u'<a href="', base, u'tag/', tag.guid, u'"',
			    c, u'>', tagfmt(clean), u'</a>')
		prt(u'<ul>')
		qc = names[:]
		for pre in [pre for pre in (u'', u'!', u'~', u'-') if pre != prefix]:
			qc[i] = pre + clean
			prt_mod(qc, tags, pre or u'+')
		prt_mod(qc[:i] + qc[i + 1:], tags[:i] + tags[i + 1:], u'X')
		prt(u'</ul></li>\n')
	prt(u'</ul>\n')

def prt_thumb(post, link=True, classname=u'thumb'):
	"""Print a single post in #thumbs view (or similar)"""
	m = post.md5
	prt(u'<span class="', classname, u'"')
	if user:
		prt(u' id="p', m, u'"')
	prt(u'>')
	if link:
		prt(u'<a href="', base, u'post/', m, u'">')
	else:
		prt(u'<span>')
	prt(u'<img ')
	prtfields((u'src', base + u'image/' + thumbsize + u'/' + m), (u'alt', m))
	prtfields((u'title', tags_as_html(post)))
	prt(u'/>')
	if link:
		prt(u'</a>')
	else:
		prt(u'</span>')
	prt(u'</span>\n')

def prt_posts(posts):
	"""Print #thumbs view"""
	prt(u'<div id="thumbs">\n')
	for post in posts:
		prt_thumb(post)
	prt(u'</div>\n')

def tags_as_html(post):
	"""Returns single string of HTML escaped tag names for post"""
	names = sorted([t.pname for t in post.tags or []])
	return u' '.join([tagfmt(n, False) for n in names])

def prt_search_form(q=u''):
	"""Print search form"""
	prt(u'<form action="', base, u'search" method="get">\n',
	    u'<div id="search-box">\n',
	    u'<input type="text" name="q" id="search-q" value="', escape(q, True),
	    u'" onfocus="WP.comp_init(this, true);" />\n',
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
	pages = range(int(ceil(float(result_count) / per_page)))
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
			prt_rel(plink, u'first')
		if p == page - 1:
			prt_rel(plink, u'prev')
		elif p == page + 1:
			prt_rel(plink, u'next')
	if pages: prt_rel(plink, u'last')
	if user:
		if pages:
			prt(u'<span class="pagelink"><a href="', link,
			    u'&amp;ALL=1">ALL</a></span>\n')
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
	    u' onfocus="WP.comp_init(this, true);" />\n',
	    u'<input type="submit" value="Tag" />\n',
	    u'</div>\n',
	    u'</form>\n')
	if client.cfg.thumbs_writeable:
		prt(u'<form action="' + base + u'post-rotate" method="post">\n',
		    u'<div id="rotate-form">\n',
		    u'<input type="hidden" name="post" value="' + m + u'" />\n',
		    u'<select name="rot">\n',
		    u'<option value="0"></option>\n',
		    u'<option value="90">Right</option>\n',
		    u'<option value="180">180°</option>\n',
		    u'<option value="270">Left</option>\n',
		    u'</select>\n',
		    u'<input type="submit" value="Rotate" />\n',
		    u'</div>\n',
		    u'</form>\n')

def prt_script(script, suffix=u'\n'):
	"""Print a script tag"""
	prt(u'<script src="', base, u'static/', script,
	    u'" type="text/javascript"></script>', suffix)

def prt_inline_script(pre, *a):
	"""Print an inline script in a both HTML and XHTML compatible manner. (The horror!)
	pre gets printed before each line, so you can indent.
	"""
	prt(pre, u'<script type="text/javascript"><!--//--><![CDATA[//><!--\n')
	prt(pre, *a)
	prt(u'\n', pre, u'//--><!]]></script>\n')

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
	prt(u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>WWWwellpapp</title>
	<meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8" />
	<link rel="stylesheet" href="%(base)sstatic/style.css" />
	<link rel="stylesheet" href="%(base)sstatic/tagstyle.css" />
	<script src="%(base)sstatic/common.js" type="text/javascript"></script>
	<link rel="help" href="%(base)sstatic/help.html" />
	<link rel="home" href="%(base)s" />\n""" % {"base": base})
	if extra_script:
		prt(u'\t')
		prt_script(extra_script)
	prt_inline_script(u'\t', u'WP.uribase = "', base, u'";')
	outdata = []
	prt(u'</head>\n<body>\n')
	if user:
		prt(u'<div id="tagbar"></div>\n')

def prt_rel(href, rel):
	"""Add a rel link to head (if appropriate)"""
	if "ALL" in fs: return
	global outdata
	real_outdata = outdata
	outdata = outdata_head
	prt(u'\t<link rel="', rel, u'" href="', href, u'" />\n')
	outdata = real_outdata

def prt_foot():
	"""Print page foot"""
	prt_script(u'complete.js')
	if user: prt_script(u'tagmode.js')
	prt(u'</body></html>')

def browser_wants_xhtml():
	"""Isn't there a library function for this?"""
	from os import environ
	if "xhtml" in fs: return True
	if "HTTP_ACCEPT" not in environ: return False
	for a in environ["HTTP_ACCEPT"].split(","):
		a = [s.strip().lower() for s in a.split(";")]
		if a[0] == "application/xhtml+xml":
			for q in a[1:]:
				if q[:3] == "q=0": return False
			return True
	return False

def finish(ctype = "text/html"):
	"""Finish up, actually sending page to client."""
	data = u''.join(outdata_head + outdata).encode("utf-8")
	ctype = str(ctype)
	if (ctype[:5] == "text/" or ctype == "application/json") and "charset" not in ctype:
		ctype += "; charset=UTF-8"
	if ctype == "text/html; charset=UTF-8" and browser_wants_xhtml():
		ctype = "application/xhtml+xml; charset=UTF-8"
		data = '<?xml version="1.0" encoding="utf-8"?>\n' + data
	print "Content-Type: " + ctype
	print "Content-Length: " + str(len(data) + 1)
	print
	print data
