var completion = {};

function init_completion(el)
{
	if (completion[el.id]) return;
	var load = document.createElement("img");
	load.className = "ajaxload";
	load.src = uribase + "static/ajaxload.gif";
	load.style.visibility = "hidden";
	el.parentNode.insertBefore(load, el.nextSibling);
	completion[el.id] = {"value": el.value, "x": null, "skip": false,
	                     "load": load, "abort": false, "tO": false,
	                     "r": null, "list": null, "complete": ""};
	el.onfocus = null;
	el.onkeypress = soon_completion_ev;
	el.onblur = remove_completion_ev;
}

function find_word(el)
{
	var start = el.selectionStart;
	var end = el.selectionEnd;
	if (!start || start != end) return "";
	var txt = el.value;
	if (end < txt.length && txt.substr(end, 1) != " ") return "";
	while (start > 0 && txt.substr(start - 1, 1) != " ") start--;
	return txt.substr(start, end - start);
}

function soon_completion(el)
{
	var c = completion[el.id];
	if (!c) return;
	if (c.tO) clearTimeout(c.tO);
	clear_completion(el);
	c.tO = setTimeout(function () { run_completion(el); }, 160);
}

function soon_completion_ev()
{
	soon_completion(this);
}

function set_complete(el, r)
{
	var alts = r.alts;
	if (!alts) return;
	if (!alts.length) {
		if (r.type) {
			alts = [r.complete];
		} else {
			return;
		}
	}
	if (alts.length == 1) {
		var word = find_word(el);
		if (word == alts[0]) return;
	}
	var old_div = document.getElementById("suggestions");
	if (old_div) {
		/* There seems to be a bug where we sometimes *
		 * still have an old one, so get rid of that. */
		document.getElementsByTagName("body")[0].removeChild(old_div);
	}
	var div = document.createElement("div");
	var c = completion[el.id];
	c.complete = r.complete;
	div.id = "suggestions";
	var pos = findpos(el);
	div.style.left = "" + pos.x + "px";
	div.style.top = "" + pos.y + "px";
	div.style.minWidth = "" + el.offsetWidth + "px";
	if (el.id == "tagmode-tags") div.style.position = "fixed";
	var ul = document.createElement("ul");
	div.appendChild(ul);
	_foreach(alts, function (n) {
		var li = document.createElement("li");
		li.appendChild(document.createTextNode(n));
		li.onmouseover = sel_this;
		li.onclick = function (ev) {
			try {
				ev.stopPropagation();
			} catch(e) {}
			return sel_done(el, li.firstChild.data, true);
		};
		ul.appendChild(li);
	});
	document.getElementsByTagName("body")[0].appendChild(div);
	c.list = div;
	el.onkeydown = function (ev) {
		if (ev.keyCode == 40) { /* down */
			sel_move(ul, 1);
			c.skip = true;
		} else if (ev.keyCode == 38) { /* up */
			sel_move(ul, -1);
			c.skip = true;
		} else {
			c.skip = false;
		}
		return true;
	};
	el.onkeypress = function (ev) {
		var d = {"idx": -1};
		var val = "";
		var full = true;
		if (ev.keyCode == 9) { /* tab */
			d = sel_find(ul);
			if (d.idx == -1) {
				if (d.lis.length == 1) {
					d.idx = 0;
				} else {
					val = c.complete;
					full = false;
				}
			}
		} else if (ev.keyCode == 13) { /* return */
			d = sel_find(ul);
		}
		if (d.idx >= 0) {
			val = d.lis[d.idx].firstChild.data;
		}
		if (val) {
			return sel_done(el, val, full);
		}
		if (c.skip) return false;
		clear_completion(el);
		soon_completion(el);
		return true;
	};
}

function run_completion(el)
{
	var c = completion[el.id];
	if (!c) return;
	if (c.value == el.value) return;
	c.value = el.value;
	var word = find_word(el);
	if (!word) return;
	c.load.style.visibility = "visible";
	c.abort = false;
	var x = new XMLHttpRequest();
	x.open("GET", uribase + "ajax-completetag?q=" + encodeURIComponent(word));
	x.onreadystatechange = function () {
		if (c.abort) return;
		if (x.readyState != 4) return;
		c.load.style.visibility = "hidden";
		if (x.status != 200) return;
		var txt = x.responseText;
		if (txt.substr(0, 1) != "{") return;
		var r = eval("(" + txt + ")");
		c.r = r;
		set_complete(el, r);
	};
	x.send();
}

function clear_completion(el)
{
	var c = completion[el.id];
	if (c.list) {
		document.getElementsByTagName("body")[0].removeChild(c.list);
		c.list = null;
	}
	el.onkeypress = soon_completion_ev;
	el.onkeydown = null;
}

function remove_completion(el)
{
	var c = completion[el.id];
	if (!c) return;
	c.abort = true;
	if (c.x) c.x.abort();
	clear_completion(el);
}

function remove_completion_ev()
{
	var el = this;
	/* We don't want to remove it before the element that was clicked   *
	 * has had a chance to insert the text, if that's what was clicked. *
	 * (Yes, it seems we lose focus before the click registers.)        *
	 */
	setTimeout(function () { remove_completion(el); }, 140);
}

function sel_move(el, dir)
{
	var d = sel_find(el);
	var pos = d.idx + dir;
	if (d.idx >= 0) d.lis[d.idx].className = "";
	if (pos == -2) {
		d.lis[d.lis.length - 1].className = "sel";
	} else if (pos >= 0 && pos < d.lis.length) {
		d.lis[pos].className = "sel";
	}
}

function sel_find(el)
{
	var lis = el.getElementsByTagName("li");
	res = {"idx": -1, "lis": lis};
	for (var i = 0; i < lis.length; i++) {
		if (lis[i].className == "sel") {
			res.idx = i;
			break;
		}
	}
	return res;
}

function sel_this()
{
	var want = this;
	_foreach(this.parentNode.getElementsByTagName("li"), function (li) {
		if (li === want) {
			li.className = "sel";
		} else {
			li.className = "";
		}
	});
}

function sel_done(el, comp, full)
{
	var e;
	try {
		var start = el.selectionStart;
		var end = el.selectionEnd;
		var txt = el.value;
		var c = completion[el.id];
		while (start > 0 && txt.substr(start - 1, 1) != " ") start--;
		while (end < txt.length && txt.substr(end - 1, 1) != " ") end++;
		end = txt.substr(end);
		if (end.length) end = " " + end;
		txt = txt.substr(0, start) + comp;
		if (full) txt += " ";
		pos = txt.length;
		txt = txt + end;
		el.value = txt;
		el.setSelectionRange(pos, pos);
		c.value = txt;
		c.word = "";
		if (full) clear_completion(el);
		el.focus();
	} catch(e) {}
	return false;
}

function findpos(el)
{
	var x = 0;
	var y = el.offsetHeight;
	while (el) {
		x += el.offsetLeft;
		y += el.offsetTop;
		el = el.offsetParent;
	}
	return {"x": x, "y": y};
}
