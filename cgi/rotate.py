#!/usr/bin/env python

import cgitb
import re
from os import environ
from sys import exit

cgitb.enable()

def notfound():
	print "Status: 404 Not Found"
	print "Content-Type: text/html; charset=UTF-8"
	print
	print "404 Post not found"
	exit()

args = environ["PATH_INFO"][1:].split("/")
if len(args) != 2: notfound()
spec, img = args
m = re.match(r"^(\d+)x(\d+)-(\d+)$", spec)
if not m: notfound()
sh, sw, rot = m.groups()
if rot not in ("90", "180", "270"): notfound()
try:
	sh, sw = map(int, (sw, sh))
except Exception:
	notfound()
if sh <= 0 or sw <= 0: notfound()
imga = img.split(".")
if len(imga) != 2: notfound()
if not re.match(r"^[0-9a-f]{32}$", imga[0]): notfound()

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
url = "../../image/" + img

data = data % locals()

print "Content-Type: image/svg+xml"
print "Content-Length: " + str(len(data) + 1)
print
print data
