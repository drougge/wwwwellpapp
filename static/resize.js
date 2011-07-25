function resize() {
	var w;
	if (!wp.resize_state) {
		wp.resize_img = document.getElementById("main-image");
		wp.resize_div = document.getElementById("rescaled-msg");
		if (!wp.resize_img || !wp.resize_div) { return false; }
		wp.resized_msg = document.createElement("div");
		wp.resized_msg.appendChild(document.createTextNode("Image rescaled"));
		wp.resized_msg.appendChild(document.createElement("br"));
		wp.resized_msg.appendChild(document.createTextNode("click to see full size"));
		wp.resize_orgWidth = wp.resize_img.width;
		wp.resize_orgHeight = wp.resize_img.height;
		wp.resize_state = 1;
	}
	if (wp.resize_state === 1) {
		w = document.body.offsetWidth - 160;
		if (w < 128) { w = 128; }
		if (w < wp.resize_orgWidth) {
			wp.resize_img.width = w;
			wp.resize_img.height = w * wp.resize_orgHeight / wp.resize_orgWidth;
			wp.resize_state = 2;
			wp.resize_div.appendChild(wp.resized_msg);
			wp.resize_div.style.display = "inline-block";
		}
	} else {
		wp.resize_img.width = wp.resize_orgWidth;
		wp.resize_img.height = wp.resize_orgHeight;
		wp.resize_state = 1;
		wp.resize_div.style.display = "none";
		wp.resize_div.removeChild(wp.resized_msg);
	}
	return false;
}
