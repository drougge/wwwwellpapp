#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit
from common import *

name = getarg("name")
type = getarg("type")

try:
	client.add_tag(name, type)
	prt(u'OK')
except Exception:
	prt(u'Server refused')

finish("text/plain")
