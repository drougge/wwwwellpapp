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
	if n[0] in "-~!": return n[1:]
	return n
def tag_prefix(n):
	"""Get prefix of tagname (if any)"""
	if n[0] in "-~!": return n[0]
	return ''

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
	n = _zwsp_pre_re.sub('\u200b\\1', n)
	n = _zwsp_post_re.sub('\\1\u200b', n)
	n = _zwsp_nr_re.sub('\u200b\\1\u200b', n)
	n = _zwsp_re.sub('\u200b', n)
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
	prt('<ul id="tags">')
	for n, t, impl in tags:
		c = 'tag implied' if impl else 'tag'
		if t.ordered: c += ' ordered'
		prt('<li class="', c, '"><a class="tt-', t.type, '" href="',
		    base, 'tag/', t.guid, '">', n, '</a>')
		if q:
			prt('\n<ul>')
			for prefix, caption in (' ', '+'), (' -', '-'):
				qa = prefix + t.name
				link = makelink('search', ('q', q + qa))
				prt('<li><a href="', link, '">', caption, '</a></li>')
			prt('</ul>\n')
		prt('</li>\n')
	prt('</ul>')

def prt_qs(names, tags, tagaround=None):
	"""Print #query-string list"""
	def prt_mod(q, tags, caption):
		q = ' '.join([q for q, t in zip(q, tags) if t])
		link = makelink('search', ('q', q))
		prt('<li><a href="', link, '">', caption, '</a></li>')
	prt('<ul id="query-string">\n')
	for name, tag, i in zip(names, tags, range(len(tags))):
		if not tag:
			prt(' <li class="unknown">', tagfmt(name), '</li>\n')
			continue
		c = ' class="tt-' + tag.type + '"'
		prefix = tag_prefix(name)
		clean = tag_clean(name)
		if tagaround:
			prt(' <li><', tagaround, c, '>', tagfmt(name), '</', tagaround, '>')
		else:
			prt(' <li>', prefix, '<a href="', base, 'tag/', tag.guid, '"',
			    c, '>', tagfmt(clean), '</a>')
		prt('<ul>')
		qc = names[:]
		for pre in [pre for pre in ('', '!', '~', '-') if pre != prefix]:
			qc[i] = pre + clean
			prt_mod(qc, tags, pre or '+')
		prt_mod(qc[:i] + qc[i + 1:], tags[:i] + tags[i + 1:], 'X')
		prt('</ul></li>\n')
	prt('</ul>\n')

def tags_as_html(post):
	"""Returns single string of HTML escaped tag names for post"""
	tags = post.tags or {}
	names = sorted(tagfmt(t, False) for t in tags if not t.datatag)
	for dt in ('aaaaaa-aaaadt-faketg-gpspos', 'aaaaaa-aaaac8-faketg-bddate',):
		t = tags.get(dt)
		if t:
			names.append(tagfmt(t, False))
	return Markup(' ').join(names)

def prt_search_form(q=''):
	"""Print search form"""
	prt('<form action="', base, 'search" method="get">\n',
	    '<div id="search-box">\n',
	    '<input type="text" name="q" id="search-q" value="', escape(q),
	    '" onfocus="WP.comp_init(this, true);" />\n',
	    '<input type="submit" value="Search" />\n',
	    '</div>\n',
	    '</form>\n')

def makelink(fn, *args):
	"""Make a html link to fn with (field, value) pairs as arguments"""
	fn = base + fn
	if not args: return fn
	if '?' in fn:
		middle = '&'
	else:
		middle = '?'
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
		if not user: return ''
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
			add_rel("first", 0)
			add_rel("prev", page - 1)
		if page < pages[-1]:
			add_rel("next", page + 1)
			add_rel("last", pages[-1])
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
	data = ''.join(request.outdata_head + request.outdata).encode('utf-8')
	ctype = str(ctype)
	if (ctype[:5] == "text/" or ctype == "application/json") and "charset" not in ctype:
		ctype += "; charset=UTF-8"
	if ctype == "text/html; charset=UTF-8" and browser_wants_xhtml():
		ctype = "application/xhtml+xml; charset=UTF-8"
		data = '<?xml version="1.0" encoding="utf-8"?>\n' + data
	response.content_type = ctype
	return data

def makesearchlink(q, tags):
	q = ' '.join([q for q, t in zip(q, tags) if t])
	return makelink('search', ('q', q))

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
