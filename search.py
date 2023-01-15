# -*- coding: utf-8 -*-

from common import globaldata, init, per_page, makelink, pagelinks, tagcloud, tag_prefix, wanted
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
		res = client.parse_tag(name, comparison=True)
		if res:
			guid, cmp, val = res
			tag = client.get_tag(guid, with_prefix=True)
			return (tag, cmp, val)
	try:
		page = max(0, int(request.query.page))
	except Exception:
		page = 0
	q = request.query.q.strip()
	data.tagnames = qa = q.split()
	data.tags = list(map(parse_tag, qa))
	data.q = q = u' '.join(qa)
	data.cloud = []
	data.result_count = 0
	ta = []
	for i, (tag, cmp, val) in enumerate(filter(None, data.tags)):
		if cmp:
			qa[i] = tag_prefix(qa[i]) + tag.name
		ta.append((tag, cmp, val))
	if ta or not q:
		if data.user and request.query.ALL:
			range = [0, 1 << 31 - 1]
			page = -1
		else:
			range = [per_page * page, per_page * page + per_page - 1]
		order = "aaaaaa-aaaac8-faketg-bddate"
		if ta and ta[0][0].ordered:
			order = "group"
		props = DotDict()
		ga = [(t.pguid, cmp, val) for t, cmp, val in ta]
		posts = client.search_post(guids=ga, order=order, range=range, wanted=wanted, props=props)
		if posts:
			data.posts = posts
			data.result_count = props.result_count
			data.page = page
			data.pagelink = makelink(u'search', (u'q', q))
			data.pages, data.rels = pagelinks(data.pagelink, page, data.result_count)
			data.cloud = tagcloud(ga)
	return data
