#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from os import environ
from sys import exit
from common import *

m = environ["PATH_INFO"][1:]
if not re.match(r"^[0-9a-f]{32}$", m):
	notfound()

post = client.get_post(m, wanted=["width", "height", "ext", "tagname", "tagguid"], separate_implied=True)
if not post: notfound()

tags = taglist(post, False) + taglist(post, True)
rels = client.post_rels(m)
img = u'../image/' + m + u'.' + post["ext"]

prt(u"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>WWWwellpapp</title>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
	<link rel="stylesheet" href="../style.css" />
	<script src="../resize.js" type="text/javascript"></script>
</head>
<body>
""")
prt(u'<div id="main">\n')
prt(u'<div onclick="resize();" id="rescaled-msg">Image rescaled<br />click to see full size</div>\n')
prt(u'<img id="main-image" onclick="resize();" ')
prtfields((u'src', img), (u'alt', m), (u'width', post["width"]), (u'height', post["height"]))
prt(u'/>\n')
prt(u'<script type="text/javascript">resize();</script>\n')
if rels:
	prt(u'<div id="related">')
	prt(u'Related posts:')
	thumbs(rels)
	prt(u'</div>\n')
prt(u'</div>\n')
prt_tagbox(tags)
prt(u'</body></html>')

finish()
