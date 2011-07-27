/* Toggle the image between full size, and fitting window width.               *
 * MarginWidth is to make room both for the left div and a possible scrollbar. *
 * MarginHeight is to make room for a possible scrollbar.                      *
 * State is 1 for original size, 2 for fit to width and 3 for fit to height.   *
 * The message is only displayed if resizing is triggered automatically.       *
 */

(function () {
	"use strict";

	WP.size = {"marginWidth": 190, "marginHeight": 30};

	WP.size.show_msg = function () {
		WP.size.msg = document.createElement("div");
		WP.size.msg.appendChild(document.createTextNode("Image rescaled"));
		WP.size.msg.appendChild(document.createElement("br"));
		WP.size.msg.appendChild(document.createTextNode("click to change size"));
		WP.size.div.appendChild(WP.size.msg);
		WP.size.div.style.display = "block";
	};

	WP.size.toggle = function (show) {
		var iw, ih, ww, wh, did = false;
		if (document.body && document.body.offsetWidth) {
			ww = document.body.offsetWidth;
			wh = document.body.offsetHeight;
		}
		if (window.innerWidth && window.innerHeight) {
			ww = window.innerWidth;
			wh = window.innerHeight;
		}
		if (!WP.size.state) {
			WP.size.img = document.getElementById("main-image");
			WP.size.div = document.getElementById("rescaled-msg");
			if (!WP.size.img || !WP.size.div) { return false; }
			WP.size.orgWidth = WP.size.img.width;
			WP.size.orgHeight = WP.size.img.height;
			WP.size.state = 1;
		} else if (WP.size.msg) {
			WP.size.div.style.display = "none";
			WP.size.div.removeChild(WP.size.msg);
			WP.size.msg = null;
		}
		if (WP.size.state === 1) {
			iw = ww - WP.size.marginWidth;
			if (iw < 128) { iw = 128; }
			if (iw < WP.size.orgWidth) {
				WP.size.img.width = iw;
				WP.size.img.height = iw * WP.size.orgHeight / WP.size.orgWidth;
				did = true;
			}
			WP.size.state = 2;
		}
		if (!did && WP.size.state === 2) {
			ih = wh - WP.size.marginHeight;
			if (ih < 128) { ih = 128; }
			if (ih < WP.size.orgHeight) {
				WP.size.img.height = ih;
				WP.size.img.width = ih * WP.size.orgWidth / WP.size.orgHeight;
				did = true;
			}
			WP.size.state = 3;
		}
		if (!did) {
			WP.size.img.width = WP.size.orgWidth;
			WP.size.img.height = WP.size.orgHeight;
			WP.size.state = 1;
		}
		if (did && show) { WP.size.show_msg(); }
		return false;
	};
}());
