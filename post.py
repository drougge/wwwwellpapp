#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import init, globaldata, taglist, wanted
from wellpapp import Post
from bottle import get, abort, mako_view as view

@get("/post/<m:re:[0-9a-f]{32}>")
@view("post")
def r_post(m):
	client = init()
	post = client.get_post(m, wanted=wanted + ("width", "height", "imgdate", "ext", "rotate",), separate_implied=True)
	if not post: abort(404)
	data = globaldata()
	
	data.post = post
	data.q = ""
	data.extra_script = u"resize.js"
	data.tags = sorted(taglist(post, False) + taglist(post, True))
	data.rel_posts = [Post(md5=md5) for md5 in client.post_rels(m) or []]
	data.rels = []
	
	if post.rotate > 0:
		spec = u'%(width)dx%(height)d-%(rotate)d' % post
		data.svg = data.base + u'rotate/' + spec + u'/' + m + u'.' + post.ext
	
	data.ordered_tags = [t for t in post.tags if t.ordered]
	if data.ordered_tags:
		do_rel = (len(data.ordered_tags) == 1)
		for t in data.ordered_tags:
			posts = client.search_post(guids=[t.guid], order="group")
			pos = [p.md5 for p in posts].index(m)
			odata = [(u'dist2', None), (u'dist1', u'prev'), (u'dist0', None),
			         (u'dist1', u'next'), (u'dist2', None)]
			start, end = pos - 2, pos + 3
			if start < 0:
				odata = odata[-start:]
				start = 0
			t.relposts = posts[start:end]
			for p, d in zip(t.relposts, odata):
				p.reldist = d[0]
				if do_rel and d[1]:
					data.rels.append((d[1], p.md5))
	
	return data
