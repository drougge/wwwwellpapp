#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common import *
from wellpapp import Post
from bottle import route, abort

@route("/post/<m:re:[0-9a-f]{32}>")
def post(m):
	client = init()
	post = client.get_post(m, wanted=["width", "height", "ext", "tagname", "tagguid", "tagdata", "rotate"], separate_implied=True)
	if not post: abort(404)
	
	tags = taglist(post, False) + taglist(post, True)
	rels = client.post_rels(m)
	ordered_tags = [t for t in post.tags if t.ordered]
	
	prt_head(u'resize.js')
	prt(u'<div id="main">\n',
	    u'<noscript><div id="no-resize" class="msgbox">',
	    u'If you had javascript, image resizing might work',
	    u'</div></noscript>\n',
	    u'<div onclick="return WP.size.toggle(false);" id="rescaled-msg" class="msgbox"></div>\n')
	
	def prt_img(m, post, id=u'main-image'):
		img = base + u'image/' + m + u'.' + post.ext
		prt(u'<img onmousedown="return WP.size.toggle(false);" ')
		prtfields((u'src', img), (u'alt', m), (u'id', id),
		          (u'width', post.width), (u'height', post.height))
		prt(u'/>\n')
	
	if post.rotate > 0:
		spec = u'%(width)dx%(height)d-%(rotate)d' % post
		svg = base + u'rotate/' + spec + u'/' + m + u'.' + post.ext
		prt(u'<object type="image/svg+xml" id="main-image" ')
		prtfields((u'data', svg), (u'width', post.width), (u'height', post.height))
		prt(u'>\n')
		if post.rotate in (90, 270):
			post.width, post.height = post.height, post.width
		prt(u' <div>This image should be rotated, but your browser does not appear to support that.</div>\n ')
		prt_img(m, post, "fallback-image")
		prt(u'</object>\n')
	else:
		prt_img(m, post)
	prt_inline_script(u'', u'WP.size.toggle(true);')
	if rels:
		prt(u'<div id="related" class="underimg">\n',
		    u'<div>Related posts</div>\n')
		prt_posts([Post(md5=md5) for md5 in rels])
		prt(u'</div>\n')
	if ordered_tags:
		do_rel = (len(ordered_tags) == 1)
		for t in ordered_tags:
			prt(u'<div id="ordered" class="underimg">\n')
			prt(u'<div class="tt-', t.type , u'">', tagfmt(t.name), u'</div>\n')
			posts = client.search_post(guids=[t.guid], order="group")
			pos = [p.md5 for p in posts].index(m)
			data = [(u'dist2', None), (u'dist1', u'prev'), (u'dist0', None),
			        (u'dist1', u'next'), (u'dist2', None)]
			start, end = pos - 2, pos + 3
			if start < 0:
				data = data[-start:]
				start = 0
			for p, d in zip(posts[start:end], data):
				prt_thumb(p, p.md5 != m, u'thumb ' + d[0])
				if do_rel and d[1]:
					prt_rel(p.md5, d[1])
			prt(u'</div>\n')
	prt(u'</div>\n')
	prt_left_head()
	prt_search_form()
	prt_tags(sorted(tags))
	if user:
		prt_tagform(m)
	prt_left_foot()
	prt_foot()
	return finish()
