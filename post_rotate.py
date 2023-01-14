# -*- coding: utf-8 -*-

from common import init
from bottle import post, request, redirect
from wellpapp import DotDict

@post("/post-rotate")
def r_post_rotate():
	m = request.forms.post
	rot = int(request.forms.rot or 0)
	assert rot in (0, 90, 180, 270)
	if rot:
		client = init()
		post = client.get_post(m, wanted=["rotate", "ext", "width", "height"])
		props = DotDict()
		if rot in (90, 270):
			props.width, props.height = post.height, post.width
		prot = int(post.rotate)
		if prot == -1: prot = 0
		assert prot in (0, 90, 180, 270)
		rot = (prot + rot) % 360
		client.save_thumbs(m, None, post.ext, rot, True)
		props.rotate = rot
		client.modify_post(m, **props)
	redirect("post/" + m)
