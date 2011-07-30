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
prt_left_head()
prt_search_form()
tags = tagcloud([guid])
prt_tags(tags, tag.name)
prt_left_foot()
prt(u'<div id="main">\n')
prt_qs([tag.name], [tag], u'h1')
prt(u'<ul>\n')
if "alias" in tag and tag.alias:
	prt(u'<li>Aliases:\n  <ul>\n')
	for alias in sorted(tag.alias):
		prt(u'  <li>' + tagfmt(alias) + u'</li>\n')
	prt(u'  </ul>\n</li>\n')
prt(u'<li>Type: ' + tag.type + u'</li>\n')
prt(u'<li>Posts: ' + unicode(tag.posts) + u'</li>\n')
prt(u'<li>Weak posts: ' + unicode(tag.weak_posts) + u'</li>\n')
for txt, rev in ((u'Implies', False), (u'Implied by', True)):
	tags = client.tag_implies(guid, reverse=rev)
	if tags:
		prt(u'<li>' + txt)
		prt(u'<ul>')
		for n, t, prio in sorted([(tagname(t), t, prio) for t, prio in tags]):
			prt(u'<li><a href="' + base + u'tag/' + t + u'">')
			prt(tagfmt(n))
			prt(u'</a>')
			if prio: prt(u'<span class="prio">(' + unicode(prio) + u')</span>')
			prt(u'</li>')
		prt(u'</ul></li>\n')
prt(u'</ul>\n')
posts, props = client.search_post(guids=[guid], order="created", range=[0, per_page - 1], wanted=["tagname", "implied"])
if posts:
	pl = pagelinks(makelink(u'search', (u'q', tag.name)), 0, props.result_count)
	prt(pl)
	prt_posts(posts)
	prt(pl)
prt(u'</div>\n')
prt_foot()

finish()
