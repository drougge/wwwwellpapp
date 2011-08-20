#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from os import environ
from sys import exit
from common import *

guid = environ["PATH_INFO"][1:]
if not re.match(r"^(?:\w{6}-){3}\w{6}$", guid):
	notfound()

tag = client.get_tag(guid)
if not tag: notfound()

if user:
	try:
		set_prio = int(getarg("prio"))
	except Exception:
		set_prio = 0
	implies = getarg("implies", u'').strip()
	if implies and u' ' not in implies:
		implguid = client.find_tag(implies, with_prefix=True)
		if implguid:
			try:
				client.add_implies(guid, implguid, set_prio)
				implies = u''
				set_prio = 0
			except Exception:
				pass
	mod_guid = getarg("guid", u'')
	if mod_guid:
		try:
			if getarg("delete", u''):
				client.remove_implies(guid, mod_guid)
			else:
				client.add_implies(guid, mod_guid, set_prio)
		except Exception:
			pass
		set_prio = 0
	update = False
	add_alias = getarg("alias", u'').strip()
	if add_alias:
		try:
			client.add_alias(add_alias, guid)
			add_alias = u''
			update = True
		except Exception:
			pass
	rem_alias = getarg("unalias", u'')
	if rem_alias:
		try:
			client.remove_alias(rem_alias)
			update = True
		except Exception:
			pass
	new_type = getarg("type", u'')
	if new_type:
		try:
			client.mod_tag(guid, type=new_type)
			tag.type = new_type
		except Exception:
			pass
	if update:
		tag = client.get_tag(guid)

prt_head()
prt_left_head()
prt_search_form()
tags = tagcloud([guid])
prt_tags(tags, tag.name)
prt_left_foot()
prt(u'<div id="main">\n')
prt_qs([tag.name], [tag], u'h1')
prt(u'<ul id="tagdata">\n')
if tag.alias or user:
	prt(u'<li>Aliases:\n  <ul>\n')
	for alias in sorted(tag.alias or []):
		prt(u'  <li>', tagfmt(alias))
		if user:
			prt(u'<form action="', tag.guid, u'" method="post"><div>\n',
			    u'<input type="hidden" name="unalias" value="', escape(alias) ,'" />\n',
			    u'<input type="submit" value="Remove" />\n',
			    u'</div></form>\n')
		prt(u'</li>\n')
	if user:
		prt(u'<li><form action="', tag.guid, u'" method="post"><div>\n',
		    u'<input type="text" name="alias" value="', escape(add_alias) ,'" />\n',
		    u'<input type="submit" value="Add" />\n',
		    u'</div></form></li>\n')
	prt(u'  </ul>\n</li>\n')
prt(u'<li>Type: ')
if user:
	prt(u'<form action="', guid, u'" method="post"><div>\n',
	    u'<select name="type">\n')
	for tt in client.metalist(u'tagtypes'):
		prt(u'<option value="', escape(tt, True))
		if tt == tag.type:
			prt(u'" selected="selected')
		prt(u'">', escape(tt), u'</option>\n')
	prt(u'</select>\n',
	    u'<input type="submit" value="Update" />\n',
	    u'</div></form>\n')
else:
	prt(tag.type)
prt(u'</li>\n')
prt(u'<li>Posts: ' + unicode(tag.posts) + u'</li>\n')
prt(u'<li>Weak posts: ' + unicode(tag.weak_posts) + u'</li>\n')
for txt, rev in ((u'Implies', False), (u'Implied by', True)):
	tags = client.tag_implies(guid, reverse=rev) or []
	if tags or (user and not rev):
		prt(u'<li>' + txt)
		prt(u'<ul>')
		for n, t, prio in sorted([(tagname(t), t, prio) for t, prio in tags]):
			prt(u'<li><a href="' + base + u'tag/' + t + u'">')
			prt(tagfmt(n))
			prt(u'</a>')
			if user and not rev:
				prt(u'<form action="', tag.guid, u'" method="post"><div>\n',
				    u'<input type="hidden" name="guid" value="', t, u'" />\n',
				    u'<input type="text" name="prio" class="prio" value="',
				    unicode(prio) ,u'" />\n',
				    u'<input type="submit" value="Update" name="update" />\n',
				    u'<input type="submit" value="Remove" name="delete" />\n',
				    u'</div></form>\n')
			elif prio:
				prt(u'<span class="prio">(' + unicode(prio) + u')</span>')
			prt(u'</li>')
		if user and not rev:
			prt(u'<li><form action="', tag.guid, u'" method="post"><div>\n',
			    u'<input type="text" name="implies" onfocus="WP.comp_init(this, false);" value="', escape(implies) ,'" />\n',
			    u'<input type="text" name="prio" class="prio" value="', unicode(set_prio) ,u'" />\n',
			    u'<input type="submit" value="Add" />\n',
			    u'</div></form></li>\n')
		prt(u'</ul></li>\n')
prt(u'</ul>\n')
posts, props = client.search_post(guids=[guid], order="created", range=[0, per_page - 1], wanted=["tagname", "implied"])
if posts:
	pl = pagelinks(makelink(u'search', (u'q', tag.name)), 0, props.result_count)
	prt(pl)
	prt_posts(posts)
	prt(pl)
prt(u'</div>\n')
prt_foot()

finish()
