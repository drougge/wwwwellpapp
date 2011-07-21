var tagging = false;
var tagging_inited = false;

function toggle_tagmode(el)
{
	var thumbs = document.getElementsByClassName("thumb");
	var func;
	if (tagging) {
		tagging = false;
		func = function () { return true; }
	} else {
		tagging = true;
		func = tag_toggle;
	}
	for (var i = 0; i < thumbs.length; i++) {
		var t = thumbs[i];
		if (!tagging_inited) {
			var span = document.createElement("span");
			t.insertBefore(span, t.firstChild);
		}
		t.className = "thumb";
		t.onclick = func;
	}
	tagging_inited = true;
	return false;
}

function tag_toggle()
{
	if (this.className == "thumb") {
		this.className = "thumb selected";
	} else {
		this.className = "thumb";
	}
	return false;
}
