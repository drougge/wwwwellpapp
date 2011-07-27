/* Toggle the image between full size, and fitting in the window.              *
 * MarginWidth is to make room both for the left div and a possible scrollbar. *
 * MarginHeight is to make room for a possible scrollbar.                      *
 * State is 1 for full size, 2 for rescaled. (Or undefined before init.)       *
 * The message is only displayed if resizing is triggered automatically.       *
 */

(function () {
	"use strict";

	WP.size = {"marginWidth": 190, "marginHeight": 30};

	WP.size.show_msg = function () {
		WP.size.msg = document.createElement("div");
		WP.size.msg.appendChild(document.createTextNode("Image rescaled"));
		WP.size.msg.appendChild(document.createElement("br"));
		WP.size.msg.appendChild(document.createTextNode("click to see full size"));
		WP.size.div.appendChild(WP.size.msg);
		WP.size.div.style.display = "block";
	};

	WP.size.toggle = function (show) {
		var ww, wh;   // Window size
		var iw, ih;   // Rescaled image size
		var hih;      // Temp for checking height scaling
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

		iw = Math.max(ww - WP.size.marginWidth, 128);
		if (iw < WP.size.orgWidth) {
			ih = iw * WP.size.orgHeight / WP.size.orgWidth;
		} else {
			iw = WP.size.orgWidth;
			ih = WP.size.orgHeight;
		}
		hih = Math.max(wh - WP.size.marginHeight, 128);
		if (hih < WP.size.orgHeight && hih < ih) {
			ih = hih;
			iw = ih * WP.size.orgWidth / WP.size.orgHeight;
		}

		if (WP.size.state === 2 || iw === WP.size.orgWidth) {
			// We want full size or image fits as is.
			WP.size.img.width = WP.size.orgWidth;
			WP.size.img.height = WP.size.orgHeight;
			WP.size.state = 1;
		} else {
			WP.size.img.width = iw;
			WP.size.img.height = ih;
			WP.size.state = 2;
			if (show) { WP.size.show_msg(); }
		}
		return false;
	};
}());
