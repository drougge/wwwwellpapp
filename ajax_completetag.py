# -*- coding: utf-8 -*-

from itertools import chain
from os.path import commonprefix

from bottle import get, request

_fuzz_ignore = "".join(map(chr, range(33))) + "-_()[]{}.,!/\"'?<>@=+%$#|\\"
def _completefuzz(word):
	return list(filter(lambda c: c not in _fuzz_ignore, word.lower()))

def complete(client, word):
	for t, get in ("EI", lambda t: t.name), ("EAI", lambda t: t.alias[0]), \
	              ("FI", lambda t: t.name), ("FAI", lambda t: t.alias[0]):
		tags = client.find_tags(t, word)
		if len(tags) == 1:
			t = tags[0]
			return (get(t), t.type), []
		if len(tags) > 1: break
	aliases = [[(a, t.type) for a in t.alias] or [] for t in tags]
	aliases = list(chain(*aliases))
	tags = [(t.name, t.type) for t in tags]
	inc = lambda t: t[0][:len(word)] == word
	all_candidates = tags + aliases
	candidates = list(filter(inc, all_candidates))
	if not candidates:
		word = _completefuzz(word)
		inc = lambda t: _completefuzz(t[0])[:len(word)] == word
		candidates = list(filter(inc, all_candidates))
	return (commonprefix([n for n, t in candidates]), ""), candidates

@get("/ajax-completetag")
def ajax_completetag(client):
	tag = request.query.q
	full_tag, alts = complete(client, tag)
	res = {}
	if full_tag[0] or alts:
		res["complete"] = full_tag[0]
		res["type"] = full_tag[1]
		if len(alts) > 20: alts = []
		res["alts"] = alts
	return res
