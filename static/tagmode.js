WP.tm = {};

WP.tm.mkb = function (txt, func, cn) {
	var button;
	button = document.createElement("input");
	if (cn !== "exit") { WP.tm.disablable.push(button); }
	button.type = "submit";
	button.value = txt;
	button.onclick = function () {
		func();
		if (WP.tm.enabled) { WP.tm.input.focus(); }
		return false;
	};
	if (cn) { button.className = cn; }
	return button;
};

WP.tm.loop = function (func) {
	var thumbs = WP.getElementsByClassName(document, "thumb");
	WP.foreach(thumbs, func);
};

WP.tm.init = function () {
	var form, div, tags;
	if (WP.tm.enabled) { return WP.tm.disable(); }
	WP.tm.tagbar = document.getElementById("tagbar");
	if (!WP.tm.inited) {
		WP.tm.loop(function (t) {
			var span = document.createElement("span");
			t.insertBefore(span, t.firstChild);
			t.onclick = WP.tm.toggle;
			WP.foreach(t.getElementsByTagName("a"), function (a) {
				a.id = "a" + t.id.substr(1);
			});
		});
		WP.foreach(document.getElementsByTagName("a"), function (a) {
			if (!a.onclick && !a.id) { a.onclick = WP.tm.confirm; }
		});
		tags = document.getElementById("tags");
		if (tags) {
			WP.foreach(tags.getElementsByTagName("a"), function (el) {
				el.onclick = WP.tm.tagLinkClick;
			});
		}
		WP.tm.disablable = [];
		form = document.createElement("form");
		form.onsubmit = WP.tm.apply;
		form.id = "tag";
		div = document.createElement("div");
		div.id = "tmr";
		div.appendChild(WP.tm.mkb(" Apply ", WP.tm.apply, "apply"));
		WP.tm.spinner = document.createElement("img");
		WP.tm.spinner.src = WP.uribase + "static/ajaxload.gif";
		div.appendChild(WP.tm.spinner);
		div.appendChild(WP.tm.mkb("Exit tagmode", WP.tm.disable, "exit"));
		form.appendChild(div);
		div = document.createElement("div");
		div.id = "tml";
		div.appendChild(WP.tm.mkb("Select all", function () {
			WP.tm.loop(function (t) {
				t.className = "thumb selected";
			});
		}, null));
		div.appendChild(WP.tm.mkb("Select none", function () {
			WP.tm.loop(function (t) {
				t.className = "thumb";
			});
		}, null));
		div.appendChild(WP.tm.mkb("Toggle selection", function () {
			WP.tm.loop(WP.tm.toggle_i);
		}, null));

		form.appendChild(div);
		WP.tm.input = document.createElement("input");
		WP.tm.disablable.push(WP.tm.input);
		WP.tm.input.type = "text";
		WP.tm.input.id = "tagmode-tags";
		div = document.createElement("div");
		div.id = "tmt";
		div.appendChild(WP.tm.input);
		form.appendChild(div);
		WP.tm.tagbar.appendChild(form);
		WP.tm.lock_count = 0;
		WP.tm.inited = true;
	}
	if (WP.tm.saved) {
		WP.tm.loop(function (t) {
			if (WP.tm.saved[t.id]) {
				t.className = "thumb selected";
			}
		});
	}
	WP.tm.enabled = true;
	WP.tm.tagbar.style.display = "block";
	WP.tm.input.focus();
	WP.comp.init(WP.tm.input);
	return false;
};

WP.tm.confirm = function () {
	var anysel = false;
	if (!WP.tm.enabled) { return true; }
	WP.tm.loop(function (t) {
		if (t.className !== "thumb") { anysel = true; }
	});
	if (WP.tm.input.value !== "" || anysel) {
		return confirm("Leave tagmode?");
	}
	return true;
};

WP.tm.tagLinkClick = function () {
	var txt = "", val, lastc, lastc2;
	if (!WP.tm.enabled) { return true; }
	WP.foreach(this.childNodes, function (el) {
		if (el.nodeType === 3) {
			txt += el.data.replace("\u200b", "");
		}
	});
	val = WP.tm.input.value;
	if (val !== "") {
		lastc = val.substr(val.length - 1);
		if (val.length > 1) {
			lastc2 = val.substr(val.length - 2, 1);
		} else {
			lastc2 = " ";
		}
		if (lastc !== " " && (lastc2 !== " " || WP.tag_prefix(lastc) === "")) {
			val += " ";
		}
	}
	WP.tm.input.value = val + txt + " ";
	WP.tm.input.focus();
	return false;
};

WP.tm.disable = function () {
	var saved = {};
	WP.tm.loop(function (t) {
		if (t.className !== "thumb") {
			saved[t.id] = true;
			t.className = "thumb";
		}
	});
	WP.tm.saved = saved;
	WP.tm.enabled = false;
	WP.tm.tagbar.style.display = "none";
	return false;
};

WP.tm.lock = function () {
	if (!WP.tm.lock_count) {
		WP.foreach(WP.tm.disablable, function (i) {
			i.disabled = true;
		});
	}
	WP.tm.lock_count++;
};

WP.tm.unlock = function () {
	WP.tm.lock_count--;
	if (!WP.tm.lock_count) {
		WP.foreach(WP.tm.disablable, function (i) {
			i.disabled = false;
		});
	}
};

WP.tm.toggle_i = function (t) {
	if (t.className === "thumb") {
		t.className = "thumb selected";
	} else {
		t.className = "thumb";
	}
};

WP.tm.toggle = function () {
	if (!WP.tm.enabled) { return true; }
	if (WP.tm.lock_count) { return false; }
	WP.tm.toggle_i(this);
	WP.tm.input.focus();
	return false;
};

WP.tm.getSelected = function (ask) {
	var m = [];
	WP.tm.loop(function (t) {
		if (t.className !== "thumb") {
			m.push(t.id.substr(1));
		}
	});
	if (!m.length) {
		WP.tm.loop(function (t) {
			m.push(t.id.substr(1));
		});
		if (ask && m.length > 1 && !confirm("Nothing selected, apply to all?")) {
			return [];
		}
	}
	return m;
};

WP.tm.apply = function () {
	var m, data, x;
	if (WP.tm.ajax) { return false; }
	if (WP.tm.input.value === "") { return false; }
	m = WP.tm.getSelected(true);
	if (!m.length) { return false; }
	WP.tm.spinner.style.visibility = "visible";
	data = "tags=" + encodeURIComponent(WP.tm.input.value) + "&m=" + m.join("+");
	x = new XMLHttpRequest();
	WP.tm.ajax = x;
	x.open("POST", WP.uribase + "ajax-tag", true);
	x.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	x.onreadystatechange = function () {
		var txt, r;
		if (x.readyState !== 4) { return; }
		WP.tm.ajax = null;
		WP.tm.spinner.style.visibility = "hidden";
		txt = x.responseText;
		if (x.status !== 200) {
			alert("Error " + x.status + "\n\n" + txt);
			return;
		}
		if (txt.substr(0, 1) !== "{") {
			alert("Error\n\n" + txt);
			return;
		}
		r = JSON.parse(txt);
		WP.tm.applyAjax(r, true);
	};
	x.send(data);
	return false;
};

WP.tm.applyAjax = function (r, full) {
	WP.tm.loop(function (t) {
		var m, img;
		m = t.id.substr(1);
		if (r.m[m]) {
			img = t.getElementsByTagName("img")[0];
			img.title = r.m[m];
		}
	});
	if (full) {
		WP.tm.input.value = r.failed;
		if (r.msg) { alert(r.msg); }
		if (r.failed) { WP.tm.createTagInit(r.types); }
	}
};

WP.tm.createTag = function () {
	var form = this, name, type, m, data, x;
	name = form.tm_name.value;
	type = form.tm_type.value;
	m = WP.tm.getSelected(false).join("+");
	data = "name=" + encodeURIComponent(name) + "&type=" + encodeURIComponent(type) + "&m=" + m;
	form.onsubmit = function () { return false; };
	WP.foreach(form.getElementsByTagName("img"), function (img) {
		img.style.visibility = "visible";
	});
	x = new XMLHttpRequest();
	x.open("POST", WP.uribase + "ajax-tag", true);
	x.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	x.onreadystatechange = function () {
		var txt, err, r, good = true;
		if (x.readyState !== 4) { return; }
		txt = x.responseText;
		err = "Error creating tag " + name + "\n\n";
		if (x.status !== 200) {
			alert(err + x.status + "\n\n" + txt);
		} else if (txt.substr(0, 1) !== "{") {
			alert(err + txt);
		} else {
			good = true;
		}
		r = JSON.parse(txt);
		if (r.msg) {
			good = false;
			alert(err + r.msg);
		}
		if (!good) { WP.tm.createTagCancel(form); }
		form.parentNode.removeChild(form);
		WP.tm.applyAjax(r, false);
		WP.tm.unlock();
	};
	x.send(data);
	return false;
};

WP.tm.createTagCancel = function (form) {
	var txt = form.tm_name.value;
	if (WP.tm.input.value.length) { txt = " " + txt; }
	WP.tm.input.value += txt;
};

WP.tm.createTagInit = function (types) {
	WP.foreach(WP.tm.input.value.split(" "), function (n) {
		var form, div, input, sel, img;
		WP.tm.lock();
		form = document.createElement("form");
		form.onsubmit = WP.tm.createTag;
		div = document.createElement("div");
		div.className = "createtag";
		form.appendChild(div);
		div.appendChild(document.createTextNode("Create " + n + " "));
		input = document.createElement("input");
		input.type = "hidden";
		input.name = "name";
		input.value = n;
		div.appendChild(input);
		sel = document.createElement("select");
		sel.name = "type";
		form.tm_name = input;
		form.tm_type = sel;
		div.appendChild(sel);
		WP.foreach(types, function (n) {
			var opt = document.createElement("option");
			opt.value = n;
			opt.className = "tt-" + n;
			opt.appendChild(document.createTextNode(n));
			sel.appendChild(opt);
		});
		WP.foreach(["Create", "Cancel"], function (n) {
			input = document.createElement("input");
			input.type = "submit";
			input.value = n;
			div.appendChild(input);
		});
		input.onclick = function () {
			WP.tm.createTagCancel(form);
			form.parentNode.removeChild(form);
			WP.tm.unlock();
			return false;
		};
		img = document.createElement("img");
		img.src = WP.uribase + "static/ajaxload.gif";
		div.appendChild(img);
		WP.tm.tagbar.appendChild(form);
	});
	WP.tm.input.value = "";
};
