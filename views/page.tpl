<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>WWWwellpapp</title>
	<meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8" />
	<link rel="stylesheet" href="${ base }static/style.css" />
	<link rel="stylesheet" href="${ base }static/tagstyle.css" />
	${ script("common.js") }
	<link rel="help" href="${ base }static/help.html" />
	<link rel="home" href="${ base }" />
	% for rel, href in rels:
		<link rel="${ rel }" href="${ href }" />
	% endfor
	% if extra_script:
		${ script(extra_script) }
	% endif
	${ inline_script('WP.uribase = "' + base + '";') }
</head>
<body>
	% if user:
		<div id="tagbar"></div>
	% endif

	<%block name="main"/>

	${ script("complete.js") }
	% if user:
		${ script("tagmode.js") }
	% endif
</body>
</html>

<%def name="script(name)">
	<script src="${ base }static/${ name }" type="text/javascript"></script>
</%def>

<%def name="inline_script(code)">
	<script type="text/javascript"><!--//--><![CDATA[//><!--
	${ code | n }
	//--><!]]></script>
</%def>

<%def name="query_string(tagaround=None)">
	## Render the query string with modifying links at the top of the page
	<%
	if not tagnames:
		return ''
	%>
	<ul id="query-string">
		% for name, tag, i in zip(tagnames, tags, range(len(tagnames))):
			% if tag:
				<% prefix, clean = tag_prefix(name), tag_clean(name) %>
				<li>${ prefix }<a href="${ base }tag/${ tag.guid }" class="tt-${ tag.type }">${ tagfmt(clean) }</a>
				<ul>
				<% qc = tagnames[:] %>
				% for pre in [pre for pre in (u'', u'!', u'~', u'-') if pre != prefix]:
					<% qc[i] = pre + clean %>
					<li><a href="${ makesearchlink(qc, tags) }">${ pre or u'+' }</a></li>
				% endfor
				<li><a href="${ makesearchlink(qc[:i] + qc[i + 1:], tags[:i] + tags[i + 1:]) }">X</a></li>
				</ul></li>
			% else:
				<li class="unknown">${ tagfmt(name) }</li>
			% endif
		% endfor
	</ul>
</%def>

<%def name="pagelinks()">
	## Render links to pages of this search
	% if pages or user:
		<div class="pagelinks">
			<% prev = -1 %>
			% for p in pages:
				% if p != prev + 1:
					<span class="pagelink linkspace">...</span>
				% endif
				<% prev = p %>
				% if p == page:
					<span class="pagelink currentpage">${ p }</span>
				% else:
					<span class="pagelink"><a href="${ pagelink }&amp;page=${ p }">${ p }</a></span>
				% endif
			% endfor
			% if user:
				% if pages:
					<span class="pagelink"><a href="${ pagelink }&amp;ALL=1">ALL</a></span>
				% endif
				<span class="pagelink"><a href="${ base }static/jserror.html" onclick="return WP.tm_init();">Tagmode</a></span>
			% endif
		</div>
	% endif
</%def>

<%def name="post_thumb(post, link=True, classname=u'thumb')">
	## Render a single post in #thumbs view (or similar)
	<span class="${ classname }" id="p${ post.md5 }">
	% if link:
		<a href="${ base }post/${ post.md5 }">
	% else:
		<span>
	% endif
	<img src="${ base }image/${ thumbsize }/${ post.md5 }" alt="${ post.md5 }" title="${ tags_as_html(post) }" />
	% if link:
		</a>
	% else:
		</span>
	% endif
	</span>
</%def>
