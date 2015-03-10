function validation(str) {
	var forbidden = ['|','\\', '/', ':', '*', '?', '"', '<', '>'];
	
	for (var i=0; i < forbidden.length; i++) {
		if (str.indexOf(forbidden[i]) >= 0) { //If this is true, so the string is invalid.
			return false;
		}
	}
	
	return true;
}


/* For the FolderDownload page: */
function checkAndSend1() {
	var username = document.getElementById('username').value;
	
	var valid = validation(username);
	
	if (valid) {
		var url = "http://localhost:8080/Downloading?username="+username;
		window.open(url, "_self");
	} else {
		alert("The username is invalid, please enter a different one. These characters are forbidden: '|','\\', '/', ':', '*', '?', '\"', '<', '>'");
	}
}


/* For the SignUp page: */
function checkAndSend2() {
	var username = document.getElementById('username').value;
	var password = document.getElementById('password').value;
	
	var valid = validation(username) && validation(password);
	
	if (valid) {
		var x = "A";
		//var url = "http://localhost:8080/SignUpApproval.htm";
		//window.open(url, "_self");
	} else {
		alert("The username is invalid, please enter a different one. These characters are forbidden: '|','\\', '/', ':', '*', '?', '\"', '<', '>'");
	}
}

/*
Exciting. Satisfying. Period.
.
*/