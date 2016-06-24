<%inherit file="page.tpl"/>
<%block name="main">
<div id="main">
	<noscript><div id="no-resize" class="msgbox">
	If you had javascript, image resizing might work
	</div></noscript>
	<div onclick="return WP.size.toggle(false);" id="rescaled-msg" class="msgbox"></div>
	% if post.rotate > 0:
		<object type="image/svg+xml" id="main-image" data="${ svg }" width="${ post.width }" height="${ post.height }">
			<div>This image should be rotated, but your browser does not appear to support that.</div>
			${ img(post.md5, post, u"fallback-image") }
		</object>
	% else:
		${ img(post.md5, post, u"main-image") }
	% endif
	${ local.inline_script(u'WP.size.toggle(true);') }
	% if rel_posts:
		<div id="related" class="underimg">
			<div>Related posts</div>
			<div id="thumbs">
				% for rel in rel_posts:
					${ local.post_thumb(rel) }
				% endfor
			</div>
		</div>
	% endif
	% for t in ordered_tags:
		<div id="ordered" class="underimg">
			<div class="tt-${ t.type }">${ tagfmt(t.name) }</div>
			% for p in t.relposts:
				${ local.post_thumb(p, p.md5 != post.md5, u'thumb ' + p.reldist) }
			% endfor
		</div>
	% endfor
</div>
</%block>

<%block name="left">
<div id="left">
	${ local.search_form(q) }
	${ local.taglist(tags) }
	<ul id="metadata">
		<li>${ post.width } x ${ post.height }</li>
		<li>${ ' '.join(str(post.imgdate).split('T')) }</li>
		% if gps:
		<li>
			<input type="text" name="gps" value="${ post.datatags['aaaaaa-aaaadt-faketg-gpspos'].value }" />
			<div id="map">
				<noscript>No map without javascript</noscript>
			</div>
		</li>
		% endif
	</ul>
	% if user:
		${ local.tagform() }
	% endif
	<div id="help"><a href="${ base }static/help.html">Help</a></div>
</div>
% if gps:
	${ local.script("leaflet-0.7.7/leaflet.js") }
	${ local.inline_script("""
		var gps = [%f, %f];
		var osmlayer = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
		})
		var map = L.map('map', {
			center: gps,
			zoom: 10,
			layers: [osmlayer]
		})
		L.marker(gps).addTo(map);
	""" % (gps.lat, gps.lon,)) }
% endif
</%block>

<%def name="img(m, post, id)">
	## Render main image
	<img onmousedown="return WP.size.toggle(false);"
	src="${ base }image/${ m }.${ post.ext }"
	alt="${ m }"
	id="${ id }"
	width="${ post.width }"
	height="${ post.height }"
	/>
</%def>

<%def name="tagform()">
	## Render form for tagging single image
	<form action="${ base }post-tag" method="post">
	<div id="tag-form">
		<input type="hidden" name="post" value="${ post.md5 }" />
		<input type="text" name="tags" id="tag-q" onfocus="WP.comp_init(this, true);" />
		<input type="submit" value="Tag" />
	</div>
	</form>
	% if cfg.thumbs_writeable:
		<form action="${ base }post-rotate" method="post">
		<div id="rotate-form">
			<input type="hidden" name="post" value="${ post.md5 }" />
			<select name="rot">
				<option value="0"></option>
				<option value="90">Right</option>
				<option value="180">180°</option>
				<option value="270">Left</option>
			</select>
			<input type="submit" value="Rotate" />
		</div>
		</form>
	% endif
</%def>
