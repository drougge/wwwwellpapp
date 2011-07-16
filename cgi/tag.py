#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from os import environ
from sys import exit
from common import *

guid = environ["PATH_INFO"][1:]
if not re.match(r"^(?:\w{6}-){3}\w{6}$", guid):
	notfound()

tag = client.get_tag(guid)
if not tag: notfound()

prt_head()
prt(u'<div id="main">\n')
prt(u'<h1>' + tagfmt(tag["name"]) + u'</h1>')
prt(u'<ul>')
if "alias" in tag:
	prt(u'<li>Aliases:\n  <ul>\n')
	for alias in tag["alias"]:
		prt(u'  <li>' + tagfmt(alias) + u'</li>\n')
	prt(u'  </ul></li>\n')
prt(u'<li>Type: ' + tag["type"] + u'</li>\n')
prt(u'<li>Posts: ' + unicode(tag["posts"]) + u'</li>\n')
prt(u'<li>Weak posts: ' + unicode(tag["weak_posts"]) + u'</li>\n')
for txt, rev in ((u'Implies', False), (u'Implied by', True)):
	tags = client.tag_implies(guid, reverse=rev)
	if tags:
		prt(u'<li>' + txt)
		prt(u'<ul>')
		for t, prio in tags:
			prt(u'<li><a href="../tag/' + t + u'">')
			prt(tagfmt(tagname(t)))
			prt(u'</a>')
			if prio: prt(u'<span class="prio">(' + unicode(prio) + u')</span>')
			prt(u'</li>')
		prt(u'</ul>')
		prt(u'</li>')
prt(u'</ul>\n')
posts, props = client.search_post(guids=[guid], order="created", range=[0, per_page - 1], wanted=["tagname", "implied"])
prt_posts(posts)
prt(pagelinks(makelink(u'../search/', (u'pq', guid), (u'q', tag["name"])), 0, props["result_count"]))
prt(u'</div>\n')
prt_foot()

finish()
