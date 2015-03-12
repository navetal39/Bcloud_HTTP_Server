key = "OurEXsatiSFAyinG";

function Encrypt(mess) {
  var encrypted = CryptoJS.AES.encrypt(mess, key);
	return encrypted;
}

/*
function Decrypt(enc_mess) {
  var decrypted = CryptoJS.AES.decrypt(enc_mess, key);
	return decrypted;
}

/*

*/