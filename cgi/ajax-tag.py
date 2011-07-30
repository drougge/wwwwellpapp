#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit
from common import *
import json

tags = getarg("tags", u'')
name = getarg("name", u'')
if name:
	try:
		type = getarg("type")
		client.add_tag(tag_clean(name), type)
		tags = name
	except Exception:
		msg = u'Failed to create'
m = getarg("m", [], True)
full = set()
weak = set()
remove = set()
failed = []
for t in tags.split():
	tag = client.find_tag(tag_clean(t))
	if tag:
		p = tag_prefix(t)
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
		elif tag_post(p, full, weak, remove):
			p = client.get_post(p.md5)
			res[p.md5] = tags_as_html(p)
	client.end_transaction()
if not res and not msg and not failed and not (name and name[0] == '-'):
	msg = u'Nothing to do?'

res = dict(failed=u' '.join(failed), m=res, msg=msg)
if failed:
	res["types"] = tagtypes()
prt(json.dumps(res))
finish("application/json")
