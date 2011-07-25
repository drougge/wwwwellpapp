#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit
from common import *
from cgi import escape

m = getarg("post")
post = client.get_post(m)
tags = getarg("tags", "")
create = getarg("create", [], True)
ctype = getarg("ctype", [], True)
full = set()
weak = set()
remove = set()
failed = []

for n, t in zip(create, ctype):
	if t:
		client.add_tag(clean(n), t)
		tags += u' ' + n
for t in tags.split():
	tag = client.find_tag(clean(t))
	if tag:
		p = prefix(t)
		if p == "~":
			weak.add(tag)
		elif p == "-":
			remove.add(tag)
		else:
			full.add(tag)
	else:
		failed.append(escape(t, True))

tag_post(post, full, weak, remove)

if not failed:
	print "Status: 302 Moved"
	print "Location: post/" + m
	print
	exit(0)

prt_head()
prt(u'<form action="post-tag" method="post">\n')
prt(u'<div>\n')
prt(u'<p>Unknown tags. Select a type to create them, or don\'t to discard that tag.</p>\n')
tt = [escape(t, True) for t in tagtypes()]
for t in failed:
	prt(u'<p>\n')
	prt(t)
	prt(u'<input type="hidden" name="create" value="' + t + u'" />\n')
	prt(u'<select name="ctype">\n')
	prt(u'<option value="" selected="selected">Don\'t create</option>\n')
	for t in tt:
		prt(u'<option value="' + t + u'" class="tt-' + t + u'">' + t + u'</option>\n')
	prt(u'</select>\n')
	prt(u'</p>\n')
prt(u'<input type="hidden" name="post" value="' + escape(m, True) + u'" />\n')
prt(u'<p><input type="submit" value="Continue" /></p>\n')
prt(u'</div>\n')
prt(u'</form>\n')
prt_foot()
finish()