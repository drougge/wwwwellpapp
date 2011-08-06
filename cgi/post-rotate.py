#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit
from common import *
from cgi import escape
from dbclient import DotDict

def rot_done():
	print "Status: 302 Moved"
	print "Location: post/" + m
	print
	exit(0)

m = getarg("post")
rot = getarg("rot", u"0")
rot = int(rot)
if rot == 0: rot_done()
assert rot in (90, 180, 270)
post = client.get_post(m, wanted=["rotate", "ext", "width", "height"])
props = DotDict()
if rot in (90, 270):
	props.width, props.height = post.height, post.width
prot = post.rotate
if prot == -1: prot = 0
assert prot in (0, 90, 180, 270)
rot = (prot + rot) % 360
client.save_thumbs(m, None, post.ext, rot, True)
props.rotate = rot
client.modify_post(m, **props)
rot_done()
