/* I wish javascript had this for arrays and not just objects.. */
function _foreach(a, func)
{
	for (var i = 0; i < a.length; i++) {
		func(a[i]);
	}
}

function find_word(el)
{
	var start = el.selectionStart;
	var end = el.selectionEnd;
	if (!start || start != end) return "";
	var txt = el.value;
	if (end < txt.length && txt.substr(end, 1) != " ") return "";
	while (start > 0 && txt.substr(start - 1, 1) != " ") start--;
	return txt.substr(start, end - start);
}

function findpos(el)
{
	var x = 0;
	var y = 0;
	while (el) {
		x += el.offsetLeft;
		y += el.offsetTop;
		el = el.offsetParent;
	}
	return {"x": x, "y": y};
}

function tag_prefix(word)
{
	var c = word.substr(0, 1);
	if (c == "-" || c == "~" || c == "!") return c;
	return ""
}

function tag_clean(word)
{
	if (tag_prefix(word)) return word.substr(1);
	return word;
}
