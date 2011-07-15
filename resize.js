var scale_state = 0;
var orgWidth = 0, orgHeight = 0;
var scale_margin = 190;

function resize()
{
	img = document.getElementById("main-image");
	msg = document.getElementById("rescaled-msg");
	if (!img) return;
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
			msg.style.display = "inline-block";
		}
	} else {
		img.width = orgWidth;
		img.height = orgHeight;
		scale_state = 1;
		msg.style.display = "none";
	}
}
