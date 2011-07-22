#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit
from common import *
import json

tags = getarg("tags")
m = getarg("m", as_list=True)
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
res = {}
msg = u''
if full or weak or remove:
	client.begin_transaction()
	for p in map(client.get_post, m):
		if not p:
			msg = u'Posts missing?'
			continue
		post_full = set([t.guid for t in p.tags])
		post_weak = set([t.guid for t in p.weaktags])
		set_full = full.difference(post_full)
		set_weak = weak.difference(post_weak)
		set_remove_full = post_full.intersection(remove)
		set_remove_weak = post_weak.intersection(remove)
		set_remove = set_remove_full.union(set_remove_weak)
		if set_full or set_weak or set_remove:
			client.tag_post(p.md5, full_tags=set_full, weak_tags=set_weak, remove_tags=set_remove)
			p = client.get_post(p.md5)
			res[p.md5] = tags_as_html(p)
	client.end_transaction()
if not res and not msg and not failed:
	msg = u'Nothing to do?'

res = dict(failed=u' '.join(failed), m=res, msg=msg)
if failed:
	res["types"] = tagtypes()
prt(json.dumps(res))
finish("application/json")
