function validation(str) {
	/* Checks whether the string is valid according to our wills.	*/
	var forbidden = ['|','\\', '/', ':', '*', '?', '"', '<', '>'];
	
	if ((str.length < 4) || (str.length > 31)) { return false; }
	
	for (var i=0; i < forbidden.length; i++) {
		if (str.indexOf(forbidden[i]) >= 0) { //If this is true, so the string is invalid.
			return false;
		}
	}
	
	return true;
}

var sIP = location.host; /* <<<<<< This is the server's IP address. <<<<<< */
if (sIP == "") { sIP = "localhost"; } // If there is no server IP - use localhost - for checking.


function checkAndSend1() {	
	/* For the FolderDownload page: */
	var username = document.getElementById('username').value;
	
	var valid = validation(username);
	
	if (valid) {
		var url = "http://" + sIP + "/Downloading?username=" + username;
		window.open(url, "_self");
	} else {
		alert("The username is invalid or too short, please enter a different one. The length needs to be 4 to 31 characters. In addition, These characters are forbidden: '|','\\', '/', ':', '*', '?', '\"', '<', '>'");
	}
}


function checkAndSend2() {	
	/* For the SignUp page: */
	var username = document.getElementById('username').value;
	var password = document.getElementById('password').value;
	
	var valid = validation(username) && validation(password);
	
	if (valid) {
		var enc_pass = Hash(password);
		
		var url = "http://" + sIP + "/SigningUp?username=" + username + "&password=" + enc_pass;
		window.open(url, "_self");
	} else {
		alert("The username or the password is invalid or too short, please enter a different one. The length needs to be 4 to 31 characters. In addition, These characters are forbidden: '|','\\', '/', ':', '*', '?', '\"', '<', '>'");
	}
}

/*
Exciting. Satisfying. Period.
.
*/