#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import *
from bottle import get, post, request, mako_view as view
from wellpapp import Tag, DotDict

@get("/")
@get("/search")
@post("/search")
@view("search")
def r_search():
	data = globaldata()
	client = init()
	def parse_tag(name):
		tag = Tag()
		guid = client.find_tag(name, resdata=tag, with_prefix=True)
		if guid: return tag
	try:
		page = max(0, int(request.query.page))
	except Exception:
		page = 0
	q = request.query.q.strip()
	data.tagnames = qa = q.split()
	data.tags = ta = map(parse_tag, qa)
	data.q = q = u' '.join(qa)
	data.cloud = []
	data.result_count = 0
	ta = filter(None, ta)
	if ta or not q:
		if user and request.query.ALL:
			range = [0, 1 << 31 - 1]
			page = -1
		else:
			range = [per_page * page, per_page * page + per_page - 1]
		order = "aaaaaa-aaaads-faketg-create"
		if ta and ta[0].ordered:
			order = "group"
		props = DotDict()
		ga = [t.pguid for t in ta]
		posts = client.search_post(guids=ga, order=order, range=range, wanted=["tagname", "implied"], props=props)
		if posts:
			data.posts = posts
			data.result_count = props.result_count
			data.page = page
			data.pagelink = makelink(u'search', (u'q', q))
			data.pages, data.rels = pagelinks(data.pagelink, page, data.result_count)
			data.cloud = tagcloud(ga)
	return data
