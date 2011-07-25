function tagmode_mkb(txt, func, cn) {
	var button;
	button = document.createElement("input");
	if (cn !== "exit") { wp.tm_disablable.push(button); }
	button.type = "submit";
	button.value = txt;
	button.onclick = function () {
		func();
		if (wp.tagging) { wp.tm_input.focus(); }
		return false;
	};
	if (cn) { button.className = cn; }
	return button;
}

function tagmode_loop(func) {
	var thumbs = document.getElementsByClassName("thumb");
	wp_foreach(thumbs, func);
}

function tagmode_init() {
	var form, div, tags;
	if (wp.tagging) { return tagmode_disable(); }
	wp.tagbar = document.getElementById("tagbar");
	if (!wp.tm_inited) {
		tagmode_loop(function (t) {
			var span = document.createElement("span");
			t.insertBefore(span, t.firstChild);
			t.onclick = tag_toggle;
			wp_foreach(t.getElementsByTagName("a"), function (a) {
				a.id = "a" + t.id.substr(1);
			});
		});
		wp_foreach(document.getElementsByTagName("a"), function (a) {
			if (!a.onclick && !a.id) { a.onclick = tagmode_confirm; }
		});
		tags = document.getElementById("tags");
		if (tags) {
			wp_foreach(tags.getElementsByTagName("a"), function (el) {
				el.onclick = tagmode_taglinkclick;
			});
		}
		wp.tm_disablable = [];
		form = document.createElement("form");
		form.onsubmit = tagmode_apply;
		form.id = "tag";
		div = document.createElement("div");
		div.id = "tmr";
		div.appendChild(tagmode_mkb(" Apply ", tagmode_apply, "apply"));
		wp.tm_spinner = document.createElement("img");
		wp.tm_spinner.src = wp.uribase + "static/ajaxload.gif";
		div.appendChild(wp.tm_spinner);
		div.appendChild(tagmode_mkb("Exit tagmode", tagmode_disable, "exit"));
		form.appendChild(div);
		div = document.createElement("div");
		div.id = "tml";
		div.appendChild(tagmode_mkb("Select all", tagmode_select_all, null));
		div.appendChild(tagmode_mkb("Select none", tagmode_unselect_all, null));
		div.appendChild(tagmode_mkb("Toggle selection", tagmode_toggle_all, null));
		form.appendChild(div);
		wp.tm_input = document.createElement("input");
		wp.tm_disablable.push(wp.tm_input);
		wp.tm_input.type = "text";
		wp.tm_input.id = "tagmode-tags";
		div = document.createElement("div");
		div.id = "tmt";
		div.appendChild(wp.tm_input);
		form.appendChild(div);
		wp.tagbar.appendChild(form);
		wp.tm_lock = 0;
		wp.tm_inited = true;
	}
	if (wp.tm_saved) {
		tagmode_loop(function (t) {
			if (wp.tm_saved[t.id]) {
				t.className = "thumb selected";
			}
		});
	}
	wp.tagging = true;
	wp.tagbar.style.display = "block";
	wp.tm_input.focus();
	init_completion(wp.tm_input);
	return false;
}

function tagmode_confirm() {
	var anysel = false;
	if (!wp.tagging) { return true; }
	tagmode_loop(function (t) {
		if (t.className !== "thumb") { anysel = true; }
	});
	if (wp.tm_input.value !== "" || anysel) {
		return confirm("Leave tagmode?");
	}
	return true;
}

function tagmode_taglinkclick() {
	var txt = "", val, lastc, lastc2;
	if (!wp.tagging) { return true; }
	wp_foreach(this.childNodes, function (el) {
		if (el.nodeType === 3) {
			txt += el.data.replace("\u200b", "");
		}
	});
	val = wp.tm_input.value;
	if (val !== "") {
		lastc = val.substr(val.length - 1);
		if (val.length > 1) {
			lastc2 = val.substr(val.length - 2, 1);
		} else {
			lastc2 = " ";
		}
		if (lastc !== " " && (lastc2 !== " " || tag_prefix(lastc) === "")) {
			val += " ";
		}
	}
	wp.tm_input.value = val + txt + " ";
	wp.tm_input.focus();
	return false;
}

function tagmode_disable() {
	var saved = {};
	tagmode_loop(function (t) {
		if (t.className !== "thumb") {
			saved[t.id] = true;
			t.className = "thumb";
		}
	});
	wp.tm_saved = saved;
	wp.tagging = false;
	wp.tagbar.style.display = "none";
	return false;
}

function tagmode_lock() {
	if (!wp.tm_lock) {
		wp_foreach(wp.tm_disablable, function (i) {
			i.disabled = true;
		});
	}
	wp.tm_lock++;
}

function tagmode_unlock() {
	wp.tm_lock--;
	if (!wp.tm_lock) {
		wp_foreach(wp.tm_disablable, function (i) {
			i.disabled = false;
		});
	}
}

function tagmode_select_all() {
	tagmode_loop(function (t) {
		t.className = "thumb selected";
	});
}

function tagmode_unselect_all() {
	tagmode_loop(function (t) {
		t.className = "thumb";
	});
}

function tagmode_toggle_all() {
	tagmode_loop(tag_toggle_i);
}

function tag_toggle_i(t) {
	if (t.className === "thumb") {
		t.className = "thumb selected";
	} else {
		t.className = "thumb";
	}
}

function tag_toggle() {
	if (!wp.tagging) { return true; }
	if (wp.tm_lock) { return false; }
	tag_toggle_i(this);
	wp.tm_input.focus();
	return false;
}

function tagmode_getselected(ask) {
	var m = [];
	tagmode_loop(function (t) {
		if (t.className !== "thumb") {
			m.push(t.id.substr(1));
		}
	});
	if (!m.length) {
		tagmode_loop(function (t) {
			m.push(t.id.substr(1));
		});
		if (ask && m.length > 1 && !confirm("Nothing selected, apply to all?")) {
			return [];
		}
	}
	return m;
}

function tagmode_apply() {
	var m, data, x;
	if (wp.tm_ajax) { return false; }
	if (wp.tm_input.value === "") { return false; }
	m = tagmode_getselected(true);
	if (!m.length) { return false; }
	wp.tm_spinner.style.visibility = "visible";
	data = "tags=" + encodeURIComponent(wp.tm_input.value) + "&m=" + m.join("+");
	x = new XMLHttpRequest();
	wp.tm_ajax = x;
	x.open("POST", wp.uribase + "ajax-tag", true);
	x.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	x.onreadystatechange = function () {
		var txt, r;
		if (x.readyState !== 4) { return; }
		wp.tm_ajax = null;
		wp.tm_spinner.style.visibility = "hidden";
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
		tagmode_result(r, true);
	};
	x.send(data);
	return false;
}

function tagmode_result(r, full) {
	tagmode_loop(function (t) {
		var m, img;
		m = t.id.substr(1);
		if (r.m[m]) {
			img = t.getElementsByTagName("img")[0];
			img.title = r.m[m];
		}
	});
	if (full) {
		wp.tm_input.value = r.failed;
		if (r.msg) { alert(r.msg); }
		if (r.failed) { tagmode_create_init(r.types); }
	}
}

function tagmode_create() {
	var form = this, name, type, m, data, x;
	name = form.name.value;
	type = form.type.value;
	m = tagmode_getselected(false).join("+");
	data = "name=" + encodeURIComponent(name) + "&type=" + encodeURIComponent(type) + "&m=" + m;
	form.onsubmit = function () { return false; };
	wp_foreach(form.getElementsByTagName("img"), function (img) {
		img.style.visibility = "visible";
	});
	x = new XMLHttpRequest();
	x.open("POST", wp.uribase + "ajax-tag", true);
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
		if (!good) { tagmode_create_cancel_put(form); }
		form.parentNode.removeChild(form);
		tagmode_result(r, false);
		tagmode_unlock();
	};
	x.send(data);
	return false;
}

function tagmode_create_cancel_put(form) {
	var txt = form.name.value;
	if (wp.tm_input.value.length) { txt = " " + txt; }
	wp.tm_input.value += txt;
}
function tagmode_create_cancel() {
	var form = this.parentNode.parentNode;
	tagmode_create_cancel_put(form);
	form.parentNode.removeChild(form);
	tagmode_unlock();
	return false;
}

function tagmode_create_init(types) {
	wp_foreach(wp.tm_input.value.split(" "), function (n) {
		var form, div, input, sel;
		tagmode_lock();
		form = document.createElement("form");
		form.onsubmit = tagmode_create;
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
		div.appendChild(sel);
		wp_foreach(types, function (n) {
			opt = document.createElement("option");
			opt.value = n;
			opt.className = "tt-" + n;
			opt.appendChild(document.createTextNode(n));
			sel.appendChild(opt);
		});
		wp_foreach(["Create", "Cancel"], function (n) {
			input = document.createElement("input");
			input.type = "submit";
			input.value = n;
			div.appendChild(input);
		});
		input.onclick = tagmode_create_cancel;
		img = document.createElement("img");
		img.src = wp.uribase + "static/ajaxload.gif";
		div.appendChild(img);
		wp.tagbar.appendChild(form);
	});
	wp.tm_input.value = "";
}
