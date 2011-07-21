var tagging = false;
var tagging_inited = false;

function tagmode_mka(txt, func)
{
	var a = document.createElement("a");
	var txt = document.createTextNode(txt);
	a.appendChild(txt)
	a.onclick = function () {
		func();
		return false;
	}
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
		tagbar.appendChild(tagmode_mka("Select all", tagmode_select_all));
		tagbar.appendChild(tagmode_mka("Select none", tagmode_unselect_all));
		tagbar.appendChild(tagmode_mka("Toggle selection", tagmode_toggle_all));
		tagbar.appendChild(tagmode_mka("Exit tagmode", tagmode_disable));
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
