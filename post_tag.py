# -*- coding: utf-8 -*-

from common import init, globaldata, tag_clean, tag_prefix, tag_post, tagtypes
from bottle import post, request, redirect, mako_view as view

@post("/post-tag")
@view("post-tag")
def r_post_tag():
	client = init()
	m = request.forms.post
	post = client.get_post(m)
	tags = request.forms.tags
	create = [a.decode("utf-8") for a in request.forms.getall("create")]
	ctype  = [a.decode("utf-8") for a in request.forms.getall("ctype")]
	full = set()
	weak = set()
	remove = set()
	failed = []
	
	for n, t in zip(create, ctype):
		if t:
			client.add_tag(tag_clean(n), t)
			tags += u' ' + n
	for t in tags.split():
		tag = client.find_tag(tag_clean(t))
		if tag:
			p = tag_prefix(t)
			if p == "~":
				weak.add(tag)
			elif p == "-":
				remove.add(tag)
			else:
				full.add(tag)
		else:
			failed.append(t)
	
	tag_post(post, full, weak, remove)
	
	if not failed:
		redirect("post/" + m)
	
	data = globaldata()
	data.tagtypes = tagtypes()
	data.failed = failed
	data.m = m
	return data
