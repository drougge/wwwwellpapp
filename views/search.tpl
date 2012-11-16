<%inherit file="page.tpl"/>
<%block name="main">
<div id="main">
	${ local.query_string(tagnames, tags) }
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
