function checkAndSend() {
	var forbidden = ['|','\\', '/', ':', '*', '?', '"', '<', '>'];
	var username = document.getElementById('username').value;
	var valid = true;
	
	for (var i=0; i < forbidden.length; i++) {
		if (username.indexOf(forbidden[i]) >= 0) { //If this is true, so the username is invalid.
			valid = false;
			break;
		}
	}
	
	if (valid) {
		var url = "http://localhost:8080/Downloading?username="+username;
		window.open(url, "_self");
	} else {
		alert("The username is invalid, please enter a different one. These characters are forbidden: '|','\\', '/', ':', '*', '?', '\"', '<', '>'");
	}
}