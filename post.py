# -*- coding: utf-8 -*-

from common import init, globaldata, taglist, wanted, cfg
from wellpapp import Post
from bottle import get, abort, mako_view as view
import math

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
	
	width = int(post.width)
	height = int(post.height)
	scale = min(float(cfg.fallback_width or 800) / width, float(cfg.fallback_height or 600) / height, 1)
	data.initial_width = int(scale * width)
	data.initial_height = int(scale * height)
	if int(post.rotate) in (90, 270):
		data.translate_horiz = math.trunc((data.initial_width - data.initial_height) / 2.0)
		data.translate_vert = math.trunc((data.initial_height - data.initial_width) / 2.0)
		data.initial_raw_width = data.initial_height
		data.initial_raw_height = data.initial_width
	else:
		data.translate_horiz = data.translate_vert = 0
		data.initial_raw_width = data.initial_width
		data.initial_raw_height = data.initial_height

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
	
	if 'aaaaaa-aaaadt-faketg-gpspos' in post.datatags:
		data.gps = post.datatags['aaaaaa-aaaadt-faketg-gpspos'].value
	
	return data
