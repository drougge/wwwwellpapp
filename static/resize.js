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
		ww = [0];
		wh = [0];
		if (document.body) {
			ww.push(document.body.offsetWidth);
			wh.push(document.body.offsetHeight);
		}
		if (document.documentElement) {
			ww.push(document.documentElement.clientWidth);
			wh.push(document.documentElement.clientHeight);
		}
		ww.push(window.innerWidth);
		wh.push(window.innerHeight);
		ww = WP.max(ww);
		wh = WP.max(wh);
		if (ww < 1 || wh < 1) { return false; }

		if (!WP.size.state) {
			WP.size.container = document.getElementById("main-image-container");
			WP.size.img = document.getElementById("main-image");
			WP.size.div = document.getElementById("rescaled-msg");
			if (!WP.size.container || !WP.size.img || !WP.size.div) { return false; }
			WP.size.orgWidth = parseInt(WP.size.img.getAttribute("data-width"));
			WP.size.orgHeight = parseInt(WP.size.img.getAttribute("data-height"));
			WP.size.rotate = parseInt(WP.size.img.getAttribute("data-rotate"));
			WP.size.switched = (WP.size.rotate == 90 || WP.size.rotate == 270);
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
		ih = Math.round(ih);
		iw = Math.round(iw);

		if (WP.size.state === 2 || iw === WP.size.orgWidth) {
			// We want full size or image fits as is.
			iw = WP.size.orgWidth;
			ih = WP.size.orgHeight
			WP.size.state = 1;
		} else {
			WP.size.state = 2;
			if (show) { WP.size.show_msg(); }
		}
		if (WP.size.switched) {
			WP.size.img.width = ih;
			WP.size.img.height = iw;
			var horiz = Math.trunc((iw - ih) / 2);
			var vert = Math.trunc((ih - iw) / 2);
			WP.size.container.style.setProperty("--translate-horiz", horiz + "px");
			WP.size.container.style.setProperty("--translate-vert", vert + "px");
		} else {
			WP.size.img.width = iw;
			WP.size.img.height = ih;
		}
		WP.size.container.style.setProperty("--width", iw + "px");
		WP.size.container.style.setProperty("--height", ih + "px");
		// If we got here CSS variables should work, so remove the
		// fallback sizer so it doesn't overflow the regular sizer.
		var fallback = document.getElementById("fallback-sizer");
		if (fallback) { fallback.parentNode.removeChild(fallback); }
		return false;
	};
}());
