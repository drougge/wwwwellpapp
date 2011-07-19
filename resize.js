var scale_state = 0;
var orgWidth = 0, orgHeight = 0;
var scale_margin = 190;
var resized_msg = document.createElement("div");
resized_msg.appendChild(document.createTextNode("Image rescaled"));
resized_msg.appendChild(document.createElement("br"));
resized_msg.appendChild(document.createTextNode("click to see full size"));

function resize()
{
	var img = document.getElementById("main-image");
	var resized_div = document.getElementById("rescaled-msg");
	if (!img || !resized_div) return 0;
	if (scale_state == 0) {
		orgWidth = img.width;
		orgHeight = img.height;
		scale_state = 1;
	}
	if (scale_state == 1) {
		var w = window.innerWidth - scale_margin;
		if (w < 128) w = 128;
		if (w < orgWidth) {
			img.width = w;
			img.height = w * orgHeight / orgWidth;
			scale_state = 2;
			resized_div.appendChild(resized_msg);
			resized_div.style.display = "inline-block";
		}
	} else {
		img.width = orgWidth;
		img.height = orgHeight;
		scale_state = 1;
		resized_div.style.display = "none";
		resized_div.removeChild(resized_msg);
	}
	return 0;
}
