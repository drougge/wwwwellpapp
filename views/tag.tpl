<%inherit file="page.tpl"/>
<%block name="main">
<div id="main">
	${ local.query_string([tag.name], [(tag, None, None)], 'h1') }
	<ul id="tagdata">

		% if tag.alias or user:
			<li>Aliases:
			<ul>
			% for alias in sorted(tag.alias or []):
				<li>${ tagfmt(alias) }
				% if user:
					<form action="${ tag.guid }" method="post"><div>
						<input type="hidden" name="unalias" value="${ alias }" />
						<input type="submit" value="Remove" />
					</div></form>
				% endif
				</li>
			% endfor
			% if user:
				<li><form action="${ tag.guid }" method="post"><div>
					<input type="text" name="alias" value="${ add_alias }" />
					<input type="submit" value="Add" />
				</div></form></li>
			% endif
			</ul>
			</li>
		% endif

		<li>Type:
		% if user:
			<form action="${ tag.guid }" method="post"><div>
			<select name="type">
			% for tt in tagtypes:
				<option value="${ tt }"
				% if tt == tag.type:
					selected="selected"
				% endif
				>${ tt }</option>
			% endfor
			</select>
			<input type="submit" value="Update" />
			</div></form>
		% else:
			${ tag.type }
		% endif
		</li>

		% if tag.valuetype:
			<li>Valuetype: ${ tag.valuetype }</li>
		% endif

		<li>Posts: ${ tag.posts }</li>
		<li>Weak posts: ${ tag.weak_posts }</li>

		% for txt, rev, tags in (('Implies', False, implies_tags), ('Implied by', True, implied_by_tags)):
			% if tags or (user and not rev):
				<li>${ txt }
				<ul>
					% for n, t, prio in sorted([(t.name, t.guid, t.prio) for t in tags]):
						<li>
							<a href="${ base }tag/${ t }">${ tagfmt(n) }</a>
							% if user and not rev:
								<form action="${ tag.guid }" method="post"><div>
									<input type="hidden" name="guid" value="${ t }" />
									<input type="text" name="prio" class="prio" value="${ prio }" />
									<input type="submit" value="Update" name="update" />
									<input type="submit" value="Remove" name="delete" />
								</div></form>
							% elif prio:
								<span class="prio">${ prio }</span>
							% endif
						</li>
						% if user and not rev:
							<li><form action="${ tag.guid }" method="post"><div>
								<input type="text" name="implies" onfocus="WP.comp_init(this, false);" value="${ implies }" />
								<input type="text" name="prio" class="prio" value="${ set_prio }" />
								<input type="submit" value="Add" />
							</div></form></li>
						% endif
					% endfor
				</ul>
				</li>
			% endif
		% endfor
	</ul>
	% if posts:
		${ local.pagelinks() }
		<div id="thumbs">
			% for post in posts:
				${ local.post_thumb(post) }
			% endfor
		</div>
		${ local.pagelinks() }
	% else:
		<p>No results.</p>
	% endif
</div>
</%block>

<%block name="left">
<div id="left">
	${ local.search_form(q) }
	${ local.taglist(cloud, q) }
	<div id="help"><a href="${ base }static/help.html">Help</a></div>
</div>
</%block>
