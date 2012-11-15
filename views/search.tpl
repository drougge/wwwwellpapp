<%inherit file="page.tpl"/>
<%block name="main">
<div id="main">
	<%local:query_string />
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
	##%include left_head
	##%include search_form
	##%include tags
	##%include left_foot
</%block>
