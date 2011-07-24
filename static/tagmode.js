function tagmode_mka(txt, func, cn) {
	var a;
	a = document.createElement("a");
	txt = document.createTextNode(txt);
	a.appendChild(txt);
	a.onclick = function () {
		func();
		return false;
	};
	if (cn) { a.className = cn; }
	a.href = "#";
	return a;
}

function tagmode_loop(func) {
	var thumbs = document.getElementsByClassName("thumb");
	wp_foreach(thumbs, func);
}

function tagmode_init() {
	var form, div, tags;
	if (wp.tagging) { return tagmode_disable(); }
	wp.tagbar = document.getElementById("tagbar");
	if (!wp.tagging_inited) {
		tagmode_loop(function (t) {
			var span = document.createElement("span");
			t.insertBefore(span, t.firstChild);
			t.onclick = tag_toggle;
		});
		tags = document.getElementById("tags");
		if (tags) {
			wp_foreach(tags.getElementsByTagName("a"), function (el) {
				el.onclick = tagmode_taglinkclick;
			});
		}
		wp_foreach(document.getElementsByClassName("pagelinks"), function (el) {
			wp_foreach(el.getElementsByTagName("a"), function (a) {
				if (!a.onclick) { a.onclick = tagmode_confirm; }
			});
		});
		wp.tagbar.appendChild(tagmode_mka("Select all", tagmode_select_all, null));
		wp.tagbar.appendChild(tagmode_mka("Select none", tagmode_unselect_all, null));
		wp.tagbar.appendChild(tagmode_mka("Toggle selection", tagmode_toggle_all, null));
		wp.tagbar.appendChild(tagmode_mka("Apply", tagmode_apply, "apply"));
		wp.tagging_spinner = document.createElement("img");
		wp.tagging_spinner.src = wp.uribase + "static/ajaxload.gif";
		wp.tagbar.appendChild(wp.tagging_spinner);
		wp.tagbar.appendChild(tagmode_mka("Exit tagmode", tagmode_disable, "exit"));
		form = document.createElement("form");
		form.onsubmit = tagmode_apply;
		form.id = "tag";
		div = document.createElement("div");
		form.appendChild(div);
		wp.tagging_input = document.createElement("input");
		wp.tagging_input.type = "text";
		wp.tagging_input.id = "tagmode-tags";
		div.appendChild(wp.tagging_input);
		wp.tagbar.appendChild(form);
		wp.tagging_inited = true;
	}
	if (wp.tagging_saved) {
		tagmode_loop(function (t) {
			if (wp.tagging_saved[t.id]) {
				t.className = "thumb selected";
			}
		});
	}
	wp.tagging = true;
	wp.tagbar.style.display = "block";
	init_completion(wp.tagging_input);
	return false;
}

function tagmode_confirm() {
	var anysel = false;
	if (!wp.tagging) { return true; }
	tagmode_loop(function (t) {
		if (t.className !== "thumb") { anysel = true; }
	});
	if (wp.tagging_input.value !== "" || anysel) {
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
	val = wp.tagging_input.value;
	if (val !== "") {
		lastc = val.substr(val.length - 1);
		lastc2 = val.substr(val.length - 2, 1);
		if (lastc !== " " && (lastc2 !== " " || tag_prefix(lastc) === "")) {
			val += " ";
		}
	}
	wp.tagging_input.value = val + txt + " ";
	wp.tagging_input.focus();
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
	wp.tagging_saved = saved;
	wp.tagging = false;
	wp.tagbar.style.display = "none";
	return false;
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
	tag_toggle_i(this);
	return false;
}

function tagmode_apply() {
	var m = [], data, x;
	if (wp.tagging_ajax) { return false; }
	if (wp.tagging_input.value === "") { return false; }
	tagmode_loop(function (t) {
		if (t.className !== "thumb") {
			m.push(t.id.substr(1));
		}
	});
	if (!m.length && confirm("Nothing selected, apply to all?")) {
		tagmode_loop(function (t) {
			m.push(t.id.substr(1));
		});
	}
	if (!m.length) { return false; }
	wp.tagging_spinner.style.visibility = "visible";
	data = "tags=" + encodeURIComponent(wp.tagging_input.value) + "&m=" + m.join("&m=");
	x = new XMLHttpRequest();
	wp.tagging_ajax = x;
	x.open("POST", wp.uribase + "ajax-tag", true);
	x.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	x.onreadystatechange = function () {
		var txt, r;
		if (x.readyState !== 4) { return; }
		wp.tagging_ajax = null;
		wp.tagging_spinner.style.visibility = "hidden";
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
		tagmode_result(r);
	};
	x.send(data);
	return false;
}

function tagmode_result(r) {
	wp.tagging_input.value = r.failed;
	tagmode_loop(function (t) {
		var m, img;
		m = t.id.substr(1);
		if (r.m[m]) {
			img = t.getElementsByTagName("img")[0];
			img.title = r.m[m];
		}
	});
	if (r.msg) { alert(r.msg); }
	if (r.failed) { tagmode_create_init(r.types); }
}

function tagmode_create() {
	var form = this, name, type, data, x;
	name = form.name.value;
	type = form.type.value;
	data = "name=" + encodeURIComponent(name) + "&type=" + encodeURIComponent(type);
	form.onsubmit = function () { return false; };
	wp_foreach(form.getElementsByTagName("img"), function (img) {
		img.style.visibility = "visible";
	});
	x = new XMLHttpRequest();
	x.open("POST", wp.uribase + "ajax-createtag", true);
	x.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	x.onreadystatechange = function () {
		var txt, err;
		if (x.readyState !== 4) { return; }
		form.parentNode.removeChild(form);
		txt = x.responseText;
		err = "Error creating tag " + name + "\n\n";
		if (x.status !== 200) {
			alert(err + x.status + "\n\n" + txt);
			return;
		}
		if (txt.substr(0, 2) !== "OK" || txt.length > 4) {
			alert(err + txt);
			return;
		}
	};
	x.send(data);
	return false;
}

function tagmode_create_cancel() {
	var form = this.parentNode.parentNode;
	form.parentNode.removeChild(form);
	return false;
}

function tagmode_create_init(types) {
	wp_foreach(wp.tagging_input.value.split(" "), function (n) {
		var form, div, input, sel;
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
}
