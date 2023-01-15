#!/usr/bin/env python3
# -*- coding: utf-8 -*-

0_0 # Python >= 3.6 is required

from bottle import get, static_file

import search
import image
import post
import tag
import browse
import post_rotate
import ajax_completetag
import ajax_tag
import post_tag

@get("/static/<fn:path>")
def static(fn):
	return static_file(fn, root="./static/")

@get("/<fn:re:robots\.txt|favicon\.ico>")
def rootstatic(fn):
	return static_file(fn, root="./")

if __name__ == "__main__":
	from bottle import run
	from sys import argv
	run(host=argv[1], port=int(argv[2]), debug=True, reloader=True)
else:
	from bottle import default_app
	application = default_app()
