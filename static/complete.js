var completion = {};

function init_completion(el)
{
	var load = document.createElement("img");
	load.className = "ajaxload";
	load.src = uribase + "static/ajaxload.gif";
	load.style.visibility = "hidden";
	el.parentNode.insertBefore(load, el.nextSibling);
	if (completion[el.id]) {
		/* This should never happen, but it seems to happen *
		 * (in some browsers) when using forward/back.      *
		 */
		remove_completion(el);
	}
	completion[el.id] = {"value": el.value, "x": null, "skip": false,
	                     "load": load, "abort": false, "tO": false,
	                     "r": null, "list": null};
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
	c.tO = setTimeout(function () { run_completion(el); }, 110);
}

function soon_completion_ev()
{
	soon_completion(this);
}

function _noop()
{
	return true;
}

function set_complete(el, r)
{
	var alts = r.alts;
	if (!alts.length) {
		if (r.type) {
			alts = [r.complete];
		} else {
			return;
		}
	}
	var pos = findpos(el);
	var div = document.createElement("div");
	var c = completion[el.id];
	div.className = "suggestion";
	div.style.left = "" + pos.x + "px";
	div.style.top = "" + pos.y + "px";
	div.style.minWidth = "" + el.offsetWidth + "px";
	var ul = document.createElement("ul");
	div.appendChild(ul);
	_foreach(alts, function (n) {
		var li = document.createElement("li");
		li.appendChild(document.createTextNode(n));
		li.onmouseover = sel_this;
		li.onclick = function () {
			return sel_done(el, li);
		};
		ul.appendChild(li);
	});
	document.getElementsByTagName("body")[0].appendChild(div);
	c.list = div;
	/* I wouldn't think blocking keyup was a good idea, but nothing *
	 * seems to break, and firefox certainly breaks without it.     *
	 */
	el.onkeyup = function () { return false; };
	el.onkeydown = function (ev) {
		c.skip = true;
		if (ev.keyCode == 40) { /* down */
			return sel_move(ul, 1);
		} else if (ev.keyCode == 38) { /* up */
			return sel_move(ul, -1);
		}
		c.skip = false;
		return true;
	};
	el.onkeypress = function (ev) {
		if (c.skip) return false;
		if (ev.keyCode == 13 || ev.keyCode == 9) { /* return or tab */
			d = sel_find(ul);
			if (d.idx == -1 && ev.keyCode == 9 && d.lis.length == 1) {
				d.idx = 0;
			}
			if (d.idx >= 0) {
				return sel_done(el, d.lis[d.idx]);
			}
		}
		clear_completion(el);
		soon_completion(el);
		return true;
	};
}

				var cnt = 0;
function run_completion(el)
{
	var c = completion[el.id];
	if (!c) return;
	if (c.value == el.value) return;
	var word = find_word(el);
	if (!word) return;
	c.load.style.visibility = "visible";
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
				document.getElementById("qqq").innerHTML = word + " :" + cnt + txt;
				cnt++;
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
	el.onkeyup = _noop;
	el.onkeydown = _noop;
}

function remove_completion(el)
{
	var c = completion[el.id];
	if (!c) return;
	el.parentNode.removeChild(c.load);
	c.abort = true;
	if (c.x) c.x.abort();
	clear_completion(el);
	delete completion[el.id];
}

function remove_completion_ev()
{
	var el = this;
	/* We don't want to remove it before the completion inserts. */
	setTimeout(function () { remove_completion(el); }, 100);
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
	return false;
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

function sel_done(el, li)
{
	var start = el.selectionStart;
	var end = el.selectionEnd;
	var txt = el.value;
	var comp = li.firstChild.data;
	var c = completion[el.id];
	while (start > 0 && txt.substr(start - 1, 1) != " ") start--;
	while (end < txt.length && txt.substr(end - 1, 1) != " ") end++;
	txt = txt.substr(0, start) + comp + " " + txt.substr(end);
	el.value = txt;
	pos = start + comp.length + 1;
	el.selectionStart = pos;
	el.selectionEnd = pos;
	c.value = txt;
	c.word = "";
	clear_completion(el);
	el.focus();
	return false;
}

function findpos(el)
{
	var x = el.offsetLeft;
	var y = el.offsetTop + el.offsetHeight;
	while (el.offsetParent) {
		el = el.offsetParent;
		x += el.offsetLeft;
		y += el.offsetTop;
	}
	return {"x": x, "y": y};
}
