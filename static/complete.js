/* This is called when we might soon want to run completion.  *
 * It gets aborted again if the user types another character. *
 */
WP.comp.soon = function (el) {
	var c = WP.comp[el.id];
	if (!c) { return; }
	if (c.tO) { clearTimeout(c.tO); }
	WP.comp.clear(el);
	c.tO = setTimeout(function () { WP.comp.run(el); }, 160);
};

WP.comp.soon_ev = function () {
	WP.comp.soon(this);
};

/* When completions are available, handle possible selecting one by keyboard. */
WP.comp.keydown = function (ev) {
	var c = WP.comp[this.id];
	if (!c) { return; }
	if (ev.keyCode === 40) { // down
		WP.comp.move_selection(c.list, 1);
		c.skip = true;
	} else if (ev.keyCode === 38) { // up
		WP.comp.move_selection(c.list, -1);
		c.skip = true;
	} else {
		c.skip = false;
	}
	return true;
};

/* Some keys work better in keydown, some in keypress, so we look at both. */
WP.comp.keypress = function (ev) {
	var c, d, val, full;
	c = WP.comp[this.id];
	if (!c) { return; }
	d = {"idx": -1};
	val = "";
	full = true;
	if (ev.keyCode === 9) { // tab
		d = WP.comp.find_selection(c.list);
		if (d.idx === -1) {
			if (d.lis.length === 1) {
				d.idx = 0;
			} else {
				val = c.complete;
				full = false;
			}
		}
	} else if (ev.keyCode === 13) { // return
		d = WP.comp.find_selection(c.list);
	}
	if (d.idx >= 0) {
		val = d.lis[d.idx].firstChild.firstChild.data;
	}
	if (val) {
		return WP.comp.selection_insert(this, val, full);
	}
	if (c.skip) { return false; }
	WP.comp.clear(this);
	WP.comp.soon(this);
	return true;
};

/* New completion suggestions available, show them. */
WP.comp.new_alts = function (el, r) {
	var alts = r.alts, div, old_div, word, c, pos, ul;
	if (!alts) { return; }
	if (!alts.length) {
		if (r.type) {
			alts = [[r.complete, r.type]];
		} else {
			return;
		}
	}
	if (alts.length === 1) {
		word = WP.tag_clean(WP.find_word(el));
		if (word === alts[0][0]) { return; }
	}
	old_div = document.getElementById("suggestions");
	if (old_div) {
		/* There seems to be a bug where we sometimes *
		 * still have an old one, so get rid of that. */
		document.getElementsByTagName("body")[0].removeChild(old_div);
	}
	div = document.createElement("div");
	c = WP.comp[el.id];
	c.complete = r.complete;
	div.id = "suggestions";
	pos = WP.findpos(el);
	div.style.left = String(pos.x) + "px";
	div.style.top = String(pos.y + el.offsetHeight) + "px";
	div.style.minWidth = String(el.offsetWidth) + "px";
	if (el.id === "tagmode-tags") { div.style.position = "fixed"; }
	ul = document.createElement("ul");
	div.appendChild(ul);
	WP.foreach(alts, function (td) {
		var n, t, li, span;
		n = td[0];
		t = td[1];
		li = document.createElement("li");
		span = document.createElement("span");
		span.appendChild(document.createTextNode(n));
		span.className = "tt-" + t;
		li.appendChild(span);
		li.onmouseover = WP.comp.select_this;
		li.onclick = function (ev) {
			try {
				ev.stopPropagation();
			} catch (e) {}
			return WP.comp.selection_insert(el, n, true);
		};
		ul.appendChild(li);
	});
	document.getElementsByTagName("body")[0].appendChild(div);
	c.list = div;
	el.onkeydown = WP.comp.keydown;
	el.onkeypress = WP.comp.keypress;
};

/* Run completion. That is, start a request to the server. */
WP.comp.run = function (el) {
	var c, x, word;
	c = WP.comp[el.id];
	if (!c) { return; }
	if (c.value === el.value) { return; }
	c.value = el.value;
	word = WP.find_word(el);
	word = WP.tag_clean(word);
	if (word.length < 2) { return; }
	c.load.style.visibility = "visible";
	c.abort = false;
	x = new XMLHttpRequest();
	x.open("GET", WP.uribase + "ajax-completetag?q=" + encodeURIComponent(word));
	x.onreadystatechange = function () {
		var txt, r;
		if (c.abort) { return; }
		if (x.readyState !== 4) { return; }
		c.load.style.visibility = "hidden";
		c.x = null;
		if (x.status !== 200) { return; }
		txt = x.responseText;
		if (txt.substr(0, 1) !== "{") { return; }
		r = JSON.parse(txt);
		c.r = r;
		WP.comp.new_alts(el, r);
	};
	c.x = x;
	x.send();
};

/* Don't show any suggestions anymore. */
WP.comp.clear = function (el) {
	var c = WP.comp[el.id];
	if (c.list) {
		document.getElementsByTagName("body")[0].removeChild(c.list);
		c.list = null;
	}
	el.onkeypress = WP.comp.soon_ev;
	el.onkeydown = null;
};

/* Remove completion for this element, because it lost focus. */
WP.comp.remove = function (el) {
	var c = WP.comp[el.id];
	if (!c) { return; }
	c.abort = true;
	if (c.x) { c.x.abort(); }
	WP.comp.clear(el);
};

/* Move between suggestions by keyboard. */
WP.comp.move_selection = function (el, dir) {
	var d, pos;
	d = WP.comp.find_selection(el);
	pos = d.idx + dir;
	if (d.idx >= 0) { d.lis[d.idx].className = ""; }
	if (pos === -2) {
		d.lis[d.lis.length - 1].className = "sel";
	} else if (pos >= 0 && pos < d.lis.length) {
		d.lis[pos].className = "sel";
	}
};

/* Find the selected suggestion under this el. */
WP.comp.find_selection = function (el) {
	var lis, res, i;
	lis = el.getElementsByTagName("li");
	res = {"idx": -1, "lis": lis};
	for (i = 0; i < lis.length; i++) {
		if (lis[i].className === "sel") {
			res.idx = i;
			break;
		}
	}
	return res;
};

/* Select this (clicked) element. */
WP.comp.select_this = function () {
	var want = this;
	WP.foreach(this.parentNode.getElementsByTagName("li"), function (li) {
		if (li === want) {
			li.className = "sel";
		} else {
			li.className = "";
		}
	});
};

/* Insert the selected suggestion in text field. */
WP.comp.selection_insert = function (el, comp, full) {
	var start, end, txt, c, prefix, pos;
	try {
		start = el.selectionStart;
		end = el.selectionEnd;
		txt = el.value;
		c = WP.comp[el.id];
		while (start > 0 && txt.substr(start - 1, 1) !== " ") { start--; }
		while (end < txt.length && txt.substr(end - 1, 1) !== " ") { end++; }
		prefix = WP.tag_prefix(txt.substr(start, 1));
		end = txt.substr(end);
		if (end.length) { end = " " + end; }
		txt = txt.substr(0, start) + prefix + comp;
		if (full) { txt += " "; }
		pos = txt.length;
		txt = txt + end;
		el.value = txt;
		el.setSelectionRange(pos, pos);
		c.value = txt;
		c.word = "";
		if (full) { WP.comp.clear(el); }
		el.focus();
	} catch (e) {}
	return false;
};

WP.comp.init = function (el) {
	var pos, load;
	if (WP.comp[el.id]) { return; }
	try {
		el.setAttribute("autocomplete", "off");
	} catch (e) {}
	pos = WP.findpos(el);
	load = document.createElement("img");
	load.className = "ajaxload";
	load.style.left = String(pos.x + el.offsetWidth + 4) + "px";
	load.style.top = String(pos.y + 2) + "px";
	if (el.id === "tagmode-tags") { load.style.position = "fixed"; }
	load.src = WP.uribase + "static/ajaxload.gif";
	load.style.visibility = "hidden";
	document.getElementsByTagName("body")[0].appendChild(load);
	WP.comp[el.id] = {"value": el.value, "x": null, "skip": false,
	                  "load": load, "abort": false, "tO": false,
	                  "r": null, "list": null, "complete": ""};
	el.onfocus = null;
	el.onkeypress = WP.comp.soon_ev;
	/* We don't want to remove it before the element that was clicked   *
	 * has had a chance to insert the text, if that's what was clicked. *
	 * (Yes, it seems we lose focus before the click registers.)        *
	 */
	el.onblur = function () {
		var el = this;
		setTimeout(function () { WP.comp.remove(el); }, 140);
	};
};
