#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from os import environ
from sys import exit
from common import *
from cgi import escape

def parse_tag(name):
	return client.find_tag(name, with_prefix=True)

pq = None
qa = []
try:
	page = max(0, int(getarg("page")))
except Exception:
	page = 0
if "q" in fs:
	q = getarg("q")
	qa = q.split()
	if "pq" in fs:
		pq = getarg("pq")
		pqa = pq.split()
	else:
		pqa = map(parse_tag, qa)
		pq = u' '.join(filter(None, pqa))

prt_head()

if qa:
	prt(u'<div id="query-string">\n')
	for qn, pn in zip(qa, pqa):
		c = u'qword'
		if not pn: c += u' unknowntag'
		prt(u'<span class="' + c + u'">' + escape(qn) + u'</span>\n')
	prt(u'</div>\n')
	if None in pqa:
		q = u' '.join([qw for qw, pqw in zip(qa, pqa) if pqw])

if pq:
	range = [per_page * page, per_page * page + per_page - 1]
	posts, props = client.search_post(guids=filter(None, pqa), order="created", range=range, wanted=["tagname", "implied"])
	pl = pagelinks(makelink(u'../search/', (u'pq', pq), (u'q', q)), page, props["result_count"])
	prt(pl)
	prt_posts(posts)
	prt(pl)
else:
	prt(u'No query?')

prt_foot()
finish()
exit()
