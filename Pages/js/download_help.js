var sIP = location.host; /* <<<<<< This is the server's IP address. <<<<<< */
if (sIP == "") { sIP = "localhost"; } // If there is no server IP - use localhost - for checking.

function get_last_update() {
	var username = document.getElementById('username').innerHTML;
	var url = "http://" + sIP + "/public_folder?username=" + username + "&is_approved=YES";
	window.open(url, "_self");
}