#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import run, route, static_file

import search
import image
import post
import tag

@route("/static/<fn>")
def static(fn):
	return static_file(fn, root="./static/")

@route("/<fn:re:robots\.txt|favicon\.ico>")
def rootstatic(fn):
	return static_file(fn, root="./")

run(host="127.0.0.1", port=12222, debug=True, reloader=True)
