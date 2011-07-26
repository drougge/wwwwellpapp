var WP = {"comp": {}, "tm": {}};

(function () {
	"use strict";

	try {
		var x = new XMLHttpRequest();
		WP.ajax_ok = true;
	} catch (e) {}

	WP.comp_init = function (el) {
		if (WP.ajax_ok && WP.comp.init) { WP.comp.init(el); }
	};

	WP.tm_init = function () {
		if (!WP.ajax_ok) {
			alert("Sorry, tagmode doesn't work in your browser.");
		} else if (WP.tm.init) {
			WP.tm.init();
		} else {
			alert("Wait until the page has finished loading.");
		}
		return false;
	};

	/* I wish javascript had foreach for arrays, but alas, I have to *
	 * provide it myself. Does what you'd expect.                    *
	 */
	WP.foreach = function (a, func) {
		var i;
		for (i = 0; i < a.length; i++) {
			func(a[i]);
		}
	};

	/* Get the current word in a text input. */
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

	/* Find the (absolute) position of an element. */
	WP.findpos = function (el) {
		var x = 0, y = 0;
		while (el) {
			x += el.offsetLeft;
			y += el.offsetTop;
			el = el.offsetParent;
		}
		return {"x": x, "y": y};
	};

	/* Return prefix character of tagname, if any. */
	WP.tag_prefix = function (word) {
		var c = word.substr(0, 1);
		if (c === "-" || c === "~" || c === "!") { return c; }
		return "";
	};

	/* Return clean tagname, without prefix character. */
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
		WP.foreach(el.getElementsByTagName("*"), function (el) {
			if (re.test(el.className)) { a.push(el); }
		});
		return a;
	};
}());

var JSON;
if (!JSON) { JSON = {}; }
if (!JSON.parse) {
	JSON.parse = function (txt) {
		return eval("(" + txt + ")");
	};
}
