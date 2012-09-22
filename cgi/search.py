#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from os import environ
from sys import exit
from common import *
from cgi import escape
from wellpapp import Tag

def parse_tag(name):
	tag = Tag()
	guid = client.find_tag(name, resdata=tag, with_prefix=True)
	if guid: return tag

try:
	page = max(0, int(getarg("page")))
except Exception:
	page = 0
q = getarg("q", u'').strip()
qa = q.split()
q = u' '.join(qa)
ta = map(parse_tag, qa)
cloud = []

prt_head()

prt(u'<div id="main">\n')

if q: prt_qs(qa, ta)

ga = [tag_prefix(qw) + t.guid for qw, t in zip(qa, ta) if t]
if ga or not q:
	if user and "ALL" in fs:
		range = [0, 1 << 31 - 1]
		page = -1
	else:
		range = [per_page * page, per_page * page + per_page - 1]
	order = "aaaaaa-aaaads-faketg-create"
	if ga:
		if client.get_tag(tag_clean(ga[0])).ordered:
			order = "group"
	posts, props = client.search_post(guids=ga, order=order, range=range, wanted=["tagname", "implied"])
	if posts:
		pl = pagelinks(makelink(u'search', (u'q', q)), page, props.result_count)
		prt(pl)
		prt_posts(posts)
		prt(pl)
		cloud = tagcloud(ga)
	else:
		prt(u'<p>No results.</p>')
else:
	prt(u'No query?')
prt(u'</div>\n')

prt_left_head()
prt_search_form(q)
prt_tags(cloud, q)
prt_left_foot()

prt_foot()
finish()
exit()
