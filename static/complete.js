completion = {};

function init_completion(el)
{
	return; /* @@disabled */
	var load = document.createElement("img");
	load.className = "ajaxload";
	load.src = uribase + "static/ajaxload.gif";
	load.style.visibility = "hidden";
	el.parentNode.insertBefore(load, el.nextSibling);
	if (completion[el.id]) {
		/* This should never happen, but it seems to happen *
		 * (in some browsers) when using forward/back.      *
		 */
		var c = completion[el.id];
		if (c.load) c.load.parentNode.removeChild(c.load);
	}
	completion[el.id] = {"value": el.value, "x": null, "word": "",
	                     "load": load, "abort": false, "tO": false,
	                     "r": null};
	el.onkeypress = soon_completion;
	el.onblur = remove_completion;
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

function soon_completion(ev)
{
	if (ev.keyCode == 8) return;
	var el = this;
	var c = completion[el.id];
	if (c.tO) clearTimeout(c.tO);
	c.tO = setTimeout(function () { run_completion(el); }, 75);
}

function set_complete(el, r)
{
	if (r.complete) {
		var c = completion[el.id];
		var start = el.selectionStart;
		var pos = el.selectionStart;
		var end = el.selectionEnd;
		var txt = el.value;
		while (start > 0 && txt.substr(start - 1, 1) != " ") start--;
		var diff = pos - start;
		if (r.complete == txt.substr(start, diff)) return;
		var newValue = txt.substr(0, start) + r.complete;
		var end = txt.substr(end);
		if (end.length) {
			newValue += end;
		} else if (r.type) {
			newValue += " ";
			diff--;
		}
		el.value = newValue;
		el.selectionStart = pos;
		el.selectionEnd = pos + r.complete.length - diff;
		c.value = newValue;
		c.word = r.complete;
	}
}

				var cnt = 0;
function run_completion(el)
{
	var c = completion[el.id];
	if (c.value == el.value) return;
	var word = find_word(el);
	if (!word) return;
	var oword = c.word;
	c.word = word;
	if (oword.length > word.length && oword.substr(0, word.length) == word) {
		set_complete(el, c.r);
		return;
	}
	c.load.style.visibility = "visible";
	var x = new XMLHttpRequest();
	x.open("GET", uribase + "complete-tag?q=" + encodeURIComponent(word));
	x.onreadystatechange = function() {
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

function remove_completion(ev)
{
	var c = completion[this.id];
	this.parentNode.removeChild(c.load);
	c.abort = true;
	if (c.x) c.x.abort();
	delete completion[this.id];
}
