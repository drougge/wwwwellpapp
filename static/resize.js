/* Toggle the image between full size, and fitting window width.          *
 * Margin is to make room both for the left div and a possible scrollbar. *
 */

WP.size = {"margin": 160};

WP.size.toggle = function () {
	var w;
	if (!WP.size.state) {
		WP.size.img = document.getElementById("main-image");
		WP.size.div = document.getElementById("rescaled-msg");
		if (!WP.size.img || !WP.size.div) { return false; }
		WP.size.msg = document.createElement("div");
		WP.size.msg.appendChild(document.createTextNode("Image rescaled"));
		WP.size.msg.appendChild(document.createElement("br"));
		WP.size.msg.appendChild(document.createTextNode("click to see full size"));
		WP.size.orgWidth = WP.size.img.width;
		WP.size.orgHeight = WP.size.img.height;
		WP.size.state = 1;
	}
	if (WP.size.state === 1) {
		w = document.body.offsetWidth - WP.size.margin;
		if (w < 128) { w = 128; }
		if (w < WP.size.orgWidth) {
			WP.size.img.width = w;
			WP.size.img.height = w * WP.size.orgHeight / WP.size.orgWidth;
			WP.size.state = 2;
			WP.size.div.appendChild(WP.size.msg);
			WP.size.div.style.display = "inline-block";
		}
	} else {
		WP.size.img.width = WP.size.orgWidth;
		WP.size.img.height = WP.size.orgHeight;
		WP.size.state = 1;
		WP.size.div.style.display = "none";
		WP.size.div.removeChild(WP.size.msg);
	}
	return false;
};
