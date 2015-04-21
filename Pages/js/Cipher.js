function Hash(mess) {
	/* Hashes the message 'mess', uses an help module CryptoJS. */
  var hash = CryptoJS.SHA256(mess);
	return hash;
}

/*
Exciting. Satisfying. Period.
.
*/