function init_completion(el) {
	var pos, load;
	if (!wp.completion) { wp.completion = {}; }
	if (wp.completion[el.id]) { return; }
	pos = findpos(el);
	load = document.createElement("img");
	load.className = "ajaxload";
	load.style.left = String(pos.x + el.offsetWidth + 4) + "px";
	load.style.top = String(pos.y + 2) + "px";
	if (el.id === "tagmode-tags") { load.style.position = "fixed"; }
	load.src = wp.uribase + "static/ajaxload.gif";
	load.style.visibility = "hidden";
	document.getElementsByTagName("body")[0].appendChild(load);
	wp.completion[el.id] = {"value": el.value, "x": null, "skip": false,
	                        "load": load, "abort": false, "tO": false,
	                        "r": null, "list": null, "complete": ""};
	el.onfocus = null;
	el.onkeypress = soon_completion_ev;
	el.onblur = remove_completion_ev;
}

function soon_completion(el) {
	var c = wp.completion[el.id];
	if (!c) { return; }
	if (c.tO) { clearTimeout(c.tO); }
	clear_completion(el);
	c.tO = setTimeout(function () { run_completion(el); }, 160);
}

function soon_completion_ev() {
	soon_completion(this);
}

function comp_keydown(ev) {
	var c = wp.completion[this.id];
	if (!c) { return; }
	if (ev.keyCode === 40) { /* down */
		sel_move(c.list, 1);
		c.skip = true;
	} else if (ev.keyCode === 38) { /* up */
		sel_move(c.list, -1);
		c.skip = true;
	} else {
		c.skip = false;
	}
	return true;
}

function comp_keypress(ev) {
	var c, d, val, full;
	c = wp.completion[this.id];
	if (!c) { return; }
	d = {"idx": -1};
	val = "";
	full = true;
	if (ev.keyCode === 9) { /* tab */
		d = sel_find(c.list);
		if (d.idx === -1) {
			if (d.lis.length === 1) {
				d.idx = 0;
			} else {
				val = c.complete;
				full = false;
			}
		}
	} else if (ev.keyCode === 13) { /* return */
		d = sel_find(c.list);
	}
	if (d.idx >= 0) {
		val = d.lis[d.idx].firstChild.firstChild.data;
	}
	if (val) {
		return sel_done(this, val, full);
	}
	if (c.skip) { return false; }
	clear_completion(this);
	soon_completion(this);
	return true;
}

function set_complete(el, r) {
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
		word = tag_clean(find_word(el));
		if (word === alts[0][0]) { return; }
	}
	old_div = document.getElementById("suggestions");
	if (old_div) {
		/* There seems to be a bug where we sometimes *
		 * still have an old one, so get rid of that. */
		document.getElementsByTagName("body")[0].removeChild(old_div);
	}
	div = document.createElement("div");
	c = wp.completion[el.id];
	c.complete = r.complete;
	div.id = "suggestions";
	pos = findpos(el);
	div.style.left = String(pos.x) + "px";
	div.style.top = String(pos.y + el.offsetHeight) + "px";
	div.style.minWidth = String(el.offsetWidth) + "px";
	if (el.id === "tagmode-tags") { div.style.position = "fixed"; }
	ul = document.createElement("ul");
	div.appendChild(ul);
	wp_foreach(alts, function (td) {
		var n, t, li, span;
		n = td[0];
		t = td[1];
		li = document.createElement("li");
		span = document.createElement("span");
		span.appendChild(document.createTextNode(n));
		span.className = "tt-" + t;
		li.appendChild(span);
		li.onmouseover = sel_this;
		li.onclick = function (ev) {
			try {
				ev.stopPropagation();
			} catch (e) {}
			return sel_done(el, n, true);
		};
		ul.appendChild(li);
	});
	document.getElementsByTagName("body")[0].appendChild(div);
	c.list = div;
	el.onkeydown = comp_keydown;
	el.onkeypress = comp_keypress;
}

function run_completion(el) {
	var c, x, word;
	c = wp.completion[el.id];
	if (!c) { return; }
	if (c.value === el.value) { return; }
	c.value = el.value;
	word = find_word(el);
	word = tag_clean(word);
	if (word.length < 2) { return; }
	c.load.style.visibility = "visible";
	c.abort = false;
	x = new XMLHttpRequest();
	x.open("GET", wp.uribase + "ajax-completetag?q=" + encodeURIComponent(word));
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
		set_complete(el, r);
	};
	c.x = x;
	x.send();
}

function clear_completion(el) {
	var c = wp.completion[el.id];
	if (c.list) {
		document.getElementsByTagName("body")[0].removeChild(c.list);
		c.list = null;
	}
	el.onkeypress = soon_completion_ev;
	el.onkeydown = null;
}

function remove_completion(el) {
	var c = wp.completion[el.id];
	if (!c) { return; }
	c.abort = true;
	if (c.x) { c.x.abort(); }
	clear_completion(el);
}

function remove_completion_ev() {
	var el = this;
	/* We don't want to remove it before the element that was clicked   *
	 * has had a chance to insert the text, if that's what was clicked. *
	 * (Yes, it seems we lose focus before the click registers.)        *
	 */
	setTimeout(function () { remove_completion(el); }, 140);
}

function sel_move(el, dir) {
	var d, pos;
	d = sel_find(el);
	pos = d.idx + dir;
	if (d.idx >= 0) { d.lis[d.idx].className = ""; }
	if (pos === -2) {
		d.lis[d.lis.length - 1].className = "sel";
	} else if (pos >= 0 && pos < d.lis.length) {
		d.lis[pos].className = "sel";
	}
}

function sel_find(el) {
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
}

function sel_this() {
	var want = this;
	wp_foreach(this.parentNode.getElementsByTagName("li"), function (li) {
		if (li === want) {
			li.className = "sel";
		} else {
			li.className = "";
		}
	});
}

function sel_done(el, comp, full) {
	var start, end, txt, c, prefix, pos;
	try {
		start = el.selectionStart;
		end = el.selectionEnd;
		txt = el.value;
		c = wp.completion[el.id];
		while (start > 0 && txt.substr(start - 1, 1) !== " ") { start--; }
		while (end < txt.length && txt.substr(end - 1, 1) !== " ") { end++; }
		prefix = tag_prefix(txt.substr(start, 1));
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
		if (full) { clear_completion(el); }
		el.focus();
	} catch (e) {}
	return false;
}
