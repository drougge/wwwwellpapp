# -*- coding: utf-8 -*-

from common import init, globaldata, tagcloud, tagname, per_page, makelink, pagelinks, wanted
from wellpapp import DotDict, ImplicationTuple
from bottle import get, post, abort, request, mako_view as view
from collections import namedtuple

ImplicationTupleWithName = namedtuple("ImplicationTupleWithName", ImplicationTuple._fields + ("name",))

def modify_tag(client, data):
	guid = data.tag.guid
	try:
		set_prio = int(request.query.prio)
	except Exception:
		set_prio = 0
	data.implies = request.query.implies.strip()
	if data.implies and u' ' not in data.implies:
		implguid = client.find_tag(data.implies, with_prefix=True)
		if implguid:
			try:
				client.add_implies(guid, implguid, set_prio)
				data.implies = u''
				set_prio = 0
			except Exception:
				pass
	mod_guid = request.query.guid
	if mod_guid:
		try:
			if request.query.delete:
				client.remove_implies(guid, mod_guid)
			else:
				client.add_implies(guid, mod_guid, set_prio)
		except Exception:
			pass
		set_prio = 0
	data.set_prio = set_prio
	update = False
	data.add_alias = request.query.alias.strip()
	if data.add_alias:
		try:
			client.add_alias(data.add_alias, guid)
			data.add_alias = u''
			update = True
		except Exception:
			pass
	rem_alias = request.query.unalias
	if rem_alias:
		try:
			client.remove_alias(rem_alias)
			update = True
		except Exception:
			pass
	new_type = request.query.type
	if new_type:
		try:
			client.mod_tag(guid, type=new_type)
			data.tag.type = new_type
		except Exception:
			pass
	if update:
		data.tag = client.get_tag(guid)

@get("/tag/<guid:re:(?:\w{6}-){3}\w{6}>")
@post("/tag/<guid:re:(?:\w{6}-){3}\w{6}>")
@view("tag")
def r_tag(guid):
	client = init()
	tag = client.get_tag(guid)
	if not tag: abort(404)
	data = globaldata()
	data.tag = tag
	
	if data.user:
		modify_tag(client, data)
	
	data.cloud = tagcloud([guid])
	data.q = tag.name
	data.tagtypes = client.metalist(u"tagtypes")
	
	def get_impl(rev):
		res = []
		for i in client.tag_implies(guid, reverse=rev) or []:
			name = tagname(i.guid)
			res.append(ImplicationTupleWithName(*(i + (name,))))
		return res
	
	data.implies_tags = get_impl(False)
	data.implied_by_tags = get_impl(True)
	
	order = "group" if tag.ordered else "aaaaaa-aaaac8-faketg-bddate"
	props = DotDict()
	posts = client.search_post(guids=[guid], order=order, range=[0, per_page - 1], wanted=wanted, props=props)
	data.posts = posts
	data.result_count = props.result_count
	data.page = 0
	if posts:
		data.pagelink = makelink(u'search', (u'q', tag.name))
		data.pages, data.rels = pagelinks(data.pagelink, 0, data.result_count)
	return data
