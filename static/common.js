var wp = {};

/* I wish javascript had this for arrays and not just objects.. */
function wp_foreach(a, func) {
	var i;
	for (i = 0; i < a.length; i++) {
		func(a[i]);
	}
}

function find_word(el) {
	var start, end, txt;
	start = el.selectionStart;
	end = el.selectionEnd;
	if (!start || start !== end) { return ""; }
	txt = el.value;
	if (end < txt.length && txt.substr(end, 1) !== " ") { return ""; }
	while (start > 0 && txt.substr(start - 1, 1) !== " ") { start--; }
	return txt.substr(start, end - start);
}

function findpos(el) {
	var x = 0, y = 0;
	while (el) {
		x += el.offsetLeft;
		y += el.offsetTop;
		el = el.offsetParent;
	}
	return {"x": x, "y": y};
}

function tag_prefix(word) {
	var c = word.substr(0, 1);
	if (c === "-" || c === "~" || c === "!") { return c; }
	return "";
}

function tag_clean(word) {
	if (tag_prefix(word)) { return word.substr(1); }
	return word;
}

/*************************************/
/* And now, the compatibility hacks. */
/*************************************/

var JSON;
if (!JSON) { JSON = {}; }
if (!JSON.parse) {
	JSON.parse = function (txt) {
		return eval("(" + txt + ")");
	};
}

function fixGetElementsByClassName(name) {
	var a = [], re;
	re = new RegExp("\\b" + name + "\\b");
	wp_foreach(document.all, function (el) {
		if (re.test(el.className)) { a.push(el); }
	});
	return a;
}

if (!document.getElementsByClassName) {
	document.constructor.prototype.getElementsByClassName = fixGetElementsByClassName;
}
