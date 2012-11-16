#!/usr/bin/env python

import re
from bottle import get, response

#@get("/rotate/<sh:int>x<sw:int>-<rot:int>/<m:re:[0-9a-f]{32}>.<ext>")
@get("/rotate/<spec:re:\d+x\d+-(?:90|180|270)>/<m:re:[0-9a-f]{32}>.<ext>")
def r_rotate(m, spec, ext):
	data = """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="100%%" height="100%%" version="1.1"
 viewBox="0 0 %(sw)d %(sh)d"
 preserveAspectRatio="xMinYMin meet"
 xmlns="http://www.w3.org/2000/svg"
 xmlns:xlink="http://www.w3.org/1999/xlink">
<image width="%(iw)d" height="%(ih)d" y="%(y)d" x="%(x)d"
 xlink:href="%(url)s" transform="rotate(%(rot)s)"/>
</svg>"""
	spec = re.match(r"^(\d+)x(\d+)-(\d+)$", spec)
	sh, sw, rot = spec.groups()
	sh, sw = map(int, (sw, sh))
	if rot == "90":
		ih, iw = sw, sh
		x = 0
		y = -ih
	elif rot == "270":
		ih, iw = sw, sh
		x = -iw
		y = 0
	else: # rot == "180"
		iw, ih = sw, sh
		x, y = -iw, -ih
	url = "../../image/" + m + "." + ext
	response.content_type = "image/svg+xml"
	return data % locals()
