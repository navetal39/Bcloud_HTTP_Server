function Encrypt(mess) {
  var hash = CryptoJS.SHA256(mess);
	return hash;
}

/*
Exciting. Satisfying. Period.
.
*/