var tagging = false;
var tagging_inited = false;
var tagging_input = null;
var tagging_ajax = null;
var tagging_img = null;

function tagmode_mka(txt, func, cn)
{
	var a = document.createElement("a");
	var txt = document.createTextNode(txt);
	a.appendChild(txt)
	a.onclick = function () {
		func();
		return false;
	}
	if (cn) a.className = cn;
	a.href = "#";
	return a;
}

/* I wish javascript had this for arrays and not just objects.. */
function _foreach(a, func)
{
	for (var i = 0; i < a.length; i++) {
		func(a[i]);
	}
}

function tagmode_loop(func)
{
	var thumbs = document.getElementsByClassName("thumb");
	_foreach(thumbs, func);
}

function tagmode_init()
{
	var tagbar = document.getElementById("tagbar");
	if (!tagging_inited) {
		tagmode_loop(function (t) {
			var span = document.createElement("span");
			t.insertBefore(span, t.firstChild);
			t.onclick = tag_toggle;
		});
		tagbar.appendChild(tagmode_mka("Select all", tagmode_select_all, null));
		tagbar.appendChild(tagmode_mka("Select none", tagmode_unselect_all, null));
		tagbar.appendChild(tagmode_mka("Toggle selection", tagmode_toggle_all, null));
		tagbar.appendChild(tagmode_mka("Apply", tagmode_apply, "apply"));
		tagging_img = document.createElement("img");
		tagging_img.src = uribase + "static/ajaxload.gif";
		tagbar.appendChild(tagging_img);
		tagbar.appendChild(tagmode_mka("Exit tagmode", tagmode_disable, "exit"));
		var form = document.createElement("form");
		form.onsubmit = tagmode_apply;
		form.id = "tag";
		var div = document.createElement("div");
		form.appendChild(div);
		tagging_input = document.createElement("input");
		tagging_input.type = "text";
		div.appendChild(tagging_input);
		tagbar.appendChild(form);
		tagging_inited = true;
		init_completion(tagging_input);
	}
	tagging = true;
	tagbar.style.display = "block";
	return false;
}

function tagmode_disable()
{
	tagging = false;
	var tagbar = document.getElementById("tagbar");
	tagbar.style.display = "none";
	tagmode_unselect_all();
	return false;
}

function tagmode_select_all()
{
	tagmode_loop(function (t) {
		t.className = "thumb selected";
	});
}

function tagmode_unselect_all()
{
	tagmode_loop(function (t) {
		t.className = "thumb";
	});
}

function tagmode_toggle_all()
{
	tagmode_loop(tag_toggle_i);
}

function tag_toggle_i(t)
{
	if (t.className == "thumb") {
		t.className = "thumb selected";
	} else {
		t.className = "thumb";
	}
}

function tag_toggle()
{
	if (!tagging) return true;
	tag_toggle_i(this);
	return false;
}

function tagmode_apply()
{
	if (tagging_ajax) return false;
	if (tagging_input.value == "") return false;
	var m = [];
	tagmode_loop(function (t) {
		if (t.className != "thumb") {
			m.push(t.id.substr(1));
		}
	});
	if (!m.length && confirm("Nothing selected, apply to all?")) {
		tagmode_loop(function (t) {
			m.push(t.id.substr(1));
		});
	}
	if (!m.length) return false;
	tagging_img.style.visibility = "visible";
	var data = "tags=" + encodeURIComponent(tagging_input.value) + "&m=" + m.join("&m=");
	var x = new XMLHttpRequest();
	tagging_ajax = x;
	x.open("POST", uribase + "ajax-tag", true);
	x.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	x.onreadystatechange = function() {
		if (x.readyState != 4) return;
		tagging_ajax = null;
		tagging_img.style.visibility = "hidden";
		var txt = x.responseText;
		if (x.status != 200) {
			alert("Error " + x.status + "\n\n" + txt);
			return;
		}
		if (txt.substr(0, 1) != "{") {
			alert("Error\n\n" + txt);
			return;
		}
		var r = eval("(" + txt + ")");
		tagmode_result(r);
	};
	x.send(data);
	return false;
}

function tagmode_result(r)
{
	tagging_input.value = r.failed;
	tagmode_loop(function (t) {
		var m = t.id.substr(1);
		if (r.m[m]) {
			var img = t.getElementsByTagName("img")[0];
			img.title = r.m[m];
		}
	});
	if (r.msg) alert(r.msg);
	if (r.failed) tagmode_create_init(r.types);
}

function tagmode_create()
{
	var form = this;
	var name = form.name.value;
	var type = form.type.value;
	var data = "name=" + encodeURIComponent(name) + "&type=" + encodeURIComponent(type);
	form.onsubmit = function () { return false; };
	_foreach(form.getElementsByTagName("img"), function (img) {
		img.style.visibility = "visible";
	});
	var x = new XMLHttpRequest();
	x.open("POST", uribase + "ajax-createtag", true);
	x.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	x.onreadystatechange = function() {
		if (x.readyState != 4) return;
		form.parentNode.removeChild(form);
		var txt = x.responseText;
		var err = "Error creating tag " + name + "\n\n";
		if (x.status != 200) {
			alert(err + x.status + "\n\n" + txt);
			return;
		}
		if (txt.substr(0, 2) != "OK" || txt.length > 4) {
			alert(err + txt);
			return;
		}
	};
	x.send(data);
	return false;
}

function tagmode_create_cancel()
{
	var form = this.parentNode.parentNode;
	form.parentNode.removeChild(form);
	return false;
}

function tagmode_create_init(types)
{
	var tagbar = document.getElementById("tagbar");
	_foreach(tagging_input.value.split(" "), function (n) {
		var form = document.createElement("form");
		form.onsubmit = tagmode_create;
		var div = document.createElement("div");
		div.className = "createtag";
		form.appendChild(div);
		div.appendChild(document.createTextNode("Create " + n + " "));
		var input = document.createElement("input");
		input.type = "hidden";
		input.name = "name";
		input.value = n;
		div.appendChild(input);
		var sel = document.createElement("select");
		sel.name = "type";
		div.appendChild(sel);
		_foreach(types, function (n) {
			opt = document.createElement("option");
			opt.value = n;
			opt.appendChild(document.createTextNode(n));
			sel.appendChild(opt);
		});
		_foreach(["Create", "Cancel"], function (n) {
			input = document.createElement("input");
			input.type = "submit";
			input.value = n;
			div.appendChild(input);
		});
		input.onclick = tagmode_create_cancel;
		img = document.createElement("img");
		img.src = uribase + "static/ajaxload.gif";
		div.appendChild(img);
		tagbar.appendChild(form);
	});
}
