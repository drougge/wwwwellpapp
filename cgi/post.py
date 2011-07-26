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
if post.rotate > 0:
	spec = u'%(width)dx%(height)d-%(rotate)d' % post
	img = base + u'rotate/' + spec + u'/' + m + u'.' + post.ext
else:
	img = base + u'image/' + m + u'.' + post.ext

prt_head(u'<script src="' + base + u'static/resize.js" type="text/javascript"></script>\n')
prt(u'<div id="main">\n')
prt(u'<noscript><div id="no-resize" class="msgbox">')
prt(u'If you had javascript, image resizing might work')
prt(u'</div></noscript>\n')
prt(u'<div onclick="return WP.size.toggle();" id="rescaled-msg" class="msgbox"></div>\n')
prt(u'<img id="main-image" onclick="return WP.size.toggle();" ')
prtfields((u'src', img), (u'alt', m), (u'width', post.width), (u'height', post.height))
prt(u'/>\n')
prt(u"""<script type="text/javascript">
<!--
WP.size.toggle();
--></script>
""")
if rels:
	prt(u'<div id="related">')
	prt(u'Related posts:')
	prt_posts([Post(md5=md5) for md5 in rels])
	prt(u'</div>\n')
prt(u'</div>\n')
prt(u'<div id="left">\n')
prt_search_form()
prt_tags(sorted(tags))
if user:
	prt_tagform(m)
prt(u'</div>\n')
prt_foot()

finish()
