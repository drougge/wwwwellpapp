#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit
from common import *
from itertools import chain
from os.path import commonprefix
import json

def complete(word):
	pre = prefix(word)
	word = clean(word)
	for t, get in ("EI", lambda t: t.name), ("EAI", lambda t: t.alias[0]):
		tags = client.find_tags(t, word).values()
		if len(tags) == 1: return pre + get(tags[0]), []
		if len(tags) > 1: break
	aliases = [t.alias or [] for t in tags]
	aliases = chain(*aliases)
	tags = [t.name for t in tags]
	inc = lambda n: n[:len(word)] == word
	candidates = filter(inc, tags) + filter(inc, aliases)
	return pre + commonprefix(candidates), candidates

tag = getarg("q")
full_tag, alts = complete(tag)
res = {}
if full_tag:
	res["complete"] = full_tag
	if not alts:
		tag = {}
		client.find_tag(full_tag, resdata=tag, with_prefix=True)
		if "type" in tag: res["type"] = tag["type"];
	if len(alts) > 20: alts = []
	res["alts"] = alts
prt(json.dumps(res));

finish("application/json")
