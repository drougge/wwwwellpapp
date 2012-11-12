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
<%!
from markupsafe import Markup
%>

<%def name="script(name)">
	<script src="${ base }static/${ name }" type="text/javascript"></script>
</%def>

<%def name="inline_script(code)">
	<script type="text/javascript"><!--//--><![CDATA[//><!--
	${ code | n }
	//--><!]]></script>
</%def>
