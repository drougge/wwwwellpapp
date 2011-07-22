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
	return a;
}

function tagmode_loop(func)
{
	var thumbs = document.getElementsByClassName("thumb");
	for (var i = 0; i < thumbs.length; i++) {
		func(thumbs[i]);
	}
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
		tagging_img.src = uribase + "ajaxload.gif";
		tagbar.appendChild(tagging_img);
		tagbar.appendChild(tagmode_mka("Exit tagmode", tagmode_disable, "exit"));
		var form = document.createElement("form");
		form.onsubmit = tagmode_apply;
		var div = document.createElement("div");
		form.appendChild(div);
		tagging_input = document.createElement("input");
		tagging_input.type = "text";
		div.appendChild(tagging_input);
		tagbar.appendChild(form);
		tagging_inited = true;
	}
	tagging = true;
	tagbar.style.display = "block";
	return false;
}

function tagmode_disable()
{
	tagging = false;
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
}
