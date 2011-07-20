#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit
from common import *

m = getarg("post")
post = client.get_post(m)
tags = getarg("tags")
full = set()
weak = set()
remove = set()
failed = []
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
		failed.append(t)
if full or weak or remove:
	client.tag_post(post.md5, full_tags=full, weak_tags=weak, remove_tags=remove)

print "Status: 302 Moved"
print "Location: post/" + m
print
