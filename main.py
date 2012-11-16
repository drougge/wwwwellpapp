#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import get, static_file

import search
import image
import post
import tag
import browse
import rotate
import post_rotate

@get("/static/<fn>")
def static(fn):
	return static_file(fn, root="./static/")

@get("/<fn:re:robots\.txt|favicon\.ico>")
def rootstatic(fn):
	return static_file(fn, root="./")

if __name__ == "__main__":
	from bottle import run
	run(host="127.0.0.1", port=12222, debug=True, reloader=True)
else:
	from bottle import default_app
	application = default_app()
