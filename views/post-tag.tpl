<%inherit file="page.tpl"/>

<%block name="main">
<form action="post-tag" method="post">
<div>
	<p>Unknown tags. Select a type to create them, or don't to discard that tag.</p>
	% for t in failed:
		<p>${ t }
		<input type="hidden" name="create" value="${ t }" />
		<select name="ctype">
		<option value="" selected="selected">Don't create</option>
		% for t in tagtypes:
			<option value="${ t }" class="tt-${ t }">${ t }</option>
		% endfor
		</select>
		</p>
	% endfor
	<input type="hidden" name="post" value="${ m }" />
	<p><input type="submit" value="Continue" /></p>
</div>
</form>
</%block>
