# -*- coding: utf-8 -*-

from markupsafe import escape, Markup
from wellpapp import Client, Config, DotDict, Tag
from urllib.parse import urlencode
import re
from math import ceil

from bottle import request, response, MakoTemplate

MakoTemplate.global_config("imports", ["from markupsafe import escape"])
MakoTemplate.global_config("default_filters", ["escape"])

def init():
	request.outdata_head = []
	request.outdata = []
	request.client = Client(cfg)
	return request.client

cfg = Config(local_rc=True)
per_page = 32
user = "fake"
base = cfg.webbase
assert base
thumbsize = cfg.thumb_sizes.split()[0]
assert thumbsize

def tag_clean(n):
	"""Get tagname without prefix"""
	if n[0] in u"-~!": return n[1:]
	return n
def tag_prefix(n):
	"""Get prefix of tagname (if any)"""
	if n[0] in u"-~!": return n[0]
	return u''

def prt(*a):
	"""Print to client.
	Conceptually at least, nothing is actually sent until finish is called.
	"""
	request.outdata.extend(a)

def prtfields(*fields):
	"""Print (fieldname, value) pairs as html attributes
	Output ends with a space.
	"""
	for f in fields:
		prt(f[0], '="', escape(f[1]), '" ')

_zwsp_pre_re = re.compile(r'([(<\[]|\b\d)')
_zwsp_post_re = re.compile(r'([:/)>\]&\\,\._-])')
_zwsp_nr_re = re.compile(r'(\d+)')
_zwsp_re = re.compile(r'\u200b+')
def tagfmt(n, html_ok=True):
	"""Format a tagname for printing in html"""
	if isinstance(n, Tag):
		if n.value is not None:
			n = '%s=%s' % (n.pname, n.value,)
		else:
			n = n.pname
	n = _zwsp_pre_re.sub(u'\u200b\\1', n)
	n = _zwsp_post_re.sub(u'\\1\u200b', n)
	n = _zwsp_nr_re.sub(u'\u200b\\1\u200b', n)
	n = _zwsp_re.sub(u'\u200b', n)
	return escape(n)

def tagname(guid):
	"""Tag guid -> name"""
	pre = tag_prefix(guid)
	tag = request.client.get_tag(tag_clean(guid))
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
	tags = request.client.find_tags("EI", "", range=range, guids=guids, order="-post", flags="-datatag")
	return [(tagfmt(t.name), t, False) for t in tags if t.guid not in guids]

def tagtypes():
	"""List of tag types."""
	return request.client.metalist("tagtypes")

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
		request.client.tag_post(p.md5, full_tags=set_full, weak_tags=set_weak, remove_tags=set_remove)
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

def tags_as_html(post):
	"""Returns single string of HTML escaped tag names for post"""
	tags = post.tags or {}
	names = sorted(tagfmt(t, False) for t in tags if not t.datatag)
	for dt in ('aaaaaa-aaaadt-faketg-gpspos', 'aaaaaa-aaaac8-faketg-bddate',):
		t = tags.get(dt)
		if t:
			names.append(tagfmt(t, False))
	return Markup(u' ').join(names)

def prt_search_form(q=u''):
	"""Print search form"""
	prt(u'<form action="', base, u'search" method="get">\n',
	    u'<div id="search-box">\n',
	    u'<input type="text" name="q" id="search-q" value="', escape(q),
	    u'" onfocus="WP.comp_init(this, true);" />\n',
	    u'<input type="submit" value="Search" />\n',
	    u'</div>\n',
	    u'</form>\n')

def makelink(fn, *args):
	"""Make a html link to fn with (field, value) pairs as arguments"""
	fn = base + fn
	if not args: return fn
	if u'?' in fn:
		middle = u'&'
	else:
		middle = u'?'
	args = urlencode([(a, v.encode("utf-8")) for a, v in args])
	return fn + middle + args

def pagelinks(link, page, result_count):
	"""Return (pages_to_link, rels).
	pages_to_link is a list of integers, rels of (rel, href) pairs.
	link is the base-link, page is current page, result_count is number
	of results we can display (not pages).
	"""
	pages = list(range(int(ceil(float(result_count) / per_page))))
	if len(pages) == 1:
		if not user: return u''
		pages = []
	if len(pages) > 16:
		if page < 8:
			pages = pages[:10] + pages[-6:]
		elif page > len(pages) - 8:
			pages = pages[:6] + pages[-10:]
		else:
			pages = pages[:6] + pages[page - 2:page + 3] + pages[-5:]
	rels = []
	if pages and not request.query.ALL:
		def add_rel(rel, p):
			rels.append((rel, link + "&page=" + str(p)))
		if page > 0:
			add_rel(u"first", 0)
			add_rel(u"prev", page - 1)
		if page < pages[-1]:
			add_rel(u"next", page + 1)
			add_rel(u"last", pages[-1])
	return pages, rels

def browser_wants_xhtml():
	"""Isn't there a library function for this?"""
	if request.query.xhtml: return True
	for a in request.headers.get("Accept", "").split(","):
		a = [s.strip().lower() for s in a.split(";")]
		if a[0] == "application/xhtml+xml":
			for q in a[1:]:
				if q[:3] == "q=0": return False
			return True
	return False

def finish(ctype = "text/html"):
	"""Finish up, actually sending page to client."""
	data = u''.join(request.outdata_head + request.outdata).encode("utf-8")
	ctype = str(ctype)
	if (ctype[:5] == "text/" or ctype == "application/json") and "charset" not in ctype:
		ctype += "; charset=UTF-8"
	if ctype == "text/html; charset=UTF-8" and browser_wants_xhtml():
		ctype = "application/xhtml+xml; charset=UTF-8"
		data = '<?xml version="1.0" encoding="utf-8"?>\n' + data
	response.content_type = ctype
	return data

def makesearchlink(q, tags):
	q = u' '.join([q for q, t in zip(q, tags) if t])
	return makelink(u'search', (u'q', q))

_globaldata = dict(user=user, tagfmt=tagfmt, tag_prefix=tag_prefix,
                   tag_clean=tag_clean, makesearchlink=makesearchlink,
                   makelink=makelink, thumbsize=thumbsize,
                   tags_as_html=tags_as_html, cfg=cfg, gps=False,
                  )
def globaldata():
	d = DotDict(_globaldata)
	d.base = request.environ["SCRIPT_NAME"].rstrip("/") + "/"
	return d

wanted = ("tagname", "tagguid", "implied", "tagdata", "datatags",)
