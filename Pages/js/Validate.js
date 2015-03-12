function validation(str) {
	var forbidden = ['|','\\', '/', ':', '*', '?', '"', '<', '>'];
	
	if (str.length < 4) { return false; }
	
	for (var i=0; i < forbidden.length; i++) {
		if (str.indexOf(forbidden[i]) >= 0) { //If this is true, so the string is invalid.
			return false;
		}
	}
	
	return true;
}

var sIP = "localhost"; /* <<<<<< This is the server's IP address. <<<<<< */

/* For the FolderDownload page: */
function checkAndSend1() {
	//var sIP = "localhost"; // This is the server's IP address.
	
	var username = document.getElementById('username').value;
	
	var valid = validation(username);
	
	if (valid) {
		var url = "http://" + sIP + ":8080/Downloading?username=" + username;
		window.open(url, "_self");
	} else {
		alert("The username is invalid or too short, please enter a different one. The minimal length is 4 characters. In addition, These characters are forbidden: '|','\\', '/', ':', '*', '?', '\"', '<', '>'");
	}
}


/* For the SignUp page: */
function checkAndSend2() {	
	var username = document.getElementById('username').value;
	var password = document.getElementById('password').value;
	
	var valid = validation(username) && validation(password);
	
	if (valid) {
		var enc_pass = Encrypt(password);//need to encrypt the password!
		
		var url = "http://" + sIP +":80/SigningUp?username=" + username + "&password=" + enc_pass;
		window.open(url, "_self");
	} else {
		alert("The username or the password is invalid or too short, please enter a different one. The minimal length is 4 characters. In addition, These characters are forbidden: '|','\\', '/', ':', '*', '?', '\"', '<', '>'");
	}
}

/*
Exciting. Satisfying. Period.
.
*/