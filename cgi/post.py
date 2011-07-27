#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from os import environ
from sys import exit
from common import *
from dbclient import Post

m = environ["PATH_INFO"][1:]
if not re.match(r"^[0-9a-f]{32}$", m):
	notfound()

post = client.get_post(m, wanted=["width", "height", "ext", "tagname", "tagguid", "tagdata", "rotate"], separate_implied=True)
if not post: notfound()

tags = taglist(post, False) + taglist(post, True)
rels = client.post_rels(m)

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
prt(u"""<script type="text/javascript">
<!--
WP.size.toggle(true);
--></script>
""")
if rels:
	prt(u'<div id="related">',
	    u'Related posts:')
	prt_posts([Post(md5=md5) for md5 in rels])
	prt(u'</div>\n')
prt(u'</div>\n',
    u'<div id="left">\n')
prt_search_form()
prt_tags(sorted(tags))
if user:
	prt_tagform(m)
prt(u'</div>\n')
prt_foot()

finish()
