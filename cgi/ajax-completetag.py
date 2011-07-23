#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit
from common import *
from itertools import chain
from os.path import commonprefix
import json

_fuzz_ignore = u"".join(map(unichr, range(33))) + u"-_()[]{}.,!/\"'?<>@=+%$#|\\"
def _completefuzz(word):
	return filter(lambda c: c not in _fuzz_ignore, word.lower())

def complete(word):
	for t, get in ("EI", lambda t: t.name), ("EAI", lambda t: t.alias[0]), \
	              ("FI", lambda t: t.name), ("FAI", lambda t: t.alias[0]):
		tags = client.find_tags(t, word).values()
		if len(tags) == 1:
			t = tags[0]
			return (get(t), t.type), []
		if len(tags) > 1: break
	aliases = [[(a, t.type) for a in t.alias] or [] for t in tags]
	aliases = chain(*aliases)
	tags = [(t.name, t.type) for t in tags]
	inc = lambda t: t[0][:len(word)] == word
	candidates = filter(inc, tags) + filter(inc, aliases)
	if not candidates:
		word = _completefuzz(word)
		inc = lambda t: _completefuzz(t[0])[:len(word)] == word
		candidates = filter(inc, tags) + filter(inc, aliases)
	return (commonprefix([n for n, t in candidates]), ""), candidates

tag = getarg("q")
full_tag, alts = complete(tag)
res = {}
if full_tag[0] or alts:
	res["complete"] = full_tag[0]
	res["type"] = full_tag[1]
	if len(alts) > 20: alts = []
	res["alts"] = alts
prt(json.dumps(res));

finish("application/json")
