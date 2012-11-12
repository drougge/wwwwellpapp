<%inherit file="page.tpl"/>
<%block name="main">
<div id="main">
	% if q:
		## prt_qs
	% endif
	% if posts:
		gah
	% else:
		<p>No results.</p>
	% endif
</div>
	##%include left_head
	##%include search_form
	##%include tags
	##%include left_foot
</%block>
