var WP = {};

/* I wish javascript had this for arrays and not just objects.. */
WP.foreach = function (a, func) {
	var i;
	for (i = 0; i < a.length; i++) {
		func(a[i]);
	}
};

WP.find_word = function (el) {
	var start, end, txt;
	start = el.selectionStart;
	end = el.selectionEnd;
	if (!start || start !== end) { return ""; }
	txt = el.value;
	if (end < txt.length && txt.substr(end, 1) !== " ") { return ""; }
	while (start > 0 && txt.substr(start - 1, 1) !== " ") { start--; }
	return txt.substr(start, end - start);
};

WP.findpos = function (el) {
	var x = 0, y = 0;
	while (el) {
		x += el.offsetLeft;
		y += el.offsetTop;
		el = el.offsetParent;
	}
	return {"x": x, "y": y};
};

WP.tag_prefix = function (word) {
	var c = word.substr(0, 1);
	if (c === "-" || c === "~" || c === "!") { return c; }
	return "";
};

WP.tag_clean = function (word) {
	if (WP.tag_prefix(word)) { return word.substr(1); }
	return word;
};

/*************************************/
/* And now, the compatibility hacks. */
/*************************************/

WP.getElementsByClassName = function (el, name) {
	var a, re;
	if (el.getElementsByClassName) {
		return el.getElementsByClassName(name);
	}
	a = [];
	re = new RegExp("\\b" + name + "\\b");
	WP.foreach(document.all, function (el) {
		if (re.test(el.className)) { a.push(el); }
	});
	return a;
};

var JSON;
if (!JSON) { JSON = {}; }
if (!JSON.parse) {
	JSON.parse = function (txt) {
		return eval("(" + txt + ")");
	};
}
