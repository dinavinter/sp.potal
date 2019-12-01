// require(["crypto-js"], function (CryptoJS) {
//     console.log(CryptoJS.HmacSHA1("Message", "Key"));
// });

import './crypto-js.js';



function base64url(source) {
    // Encode in classical base64
    var encodedSource = CryptoJS.enc.Base64.stringify(source);

    // Remove padding equal characters
    encodedSource = encodedSource.replace(/=+$/, '');

    // Replace characters according to base64url specifications
    encodedSource = encodedSource.replace(/\+/g, '-');
    encodedSource = encodedSource.replace(/\//g, '_');

    return encodedSource;
}

export default function create_client_jwt(clientId, clientSecret) {
	var iat = Math.floor(new Date().getTime() / 1000);
	var minutesToAdd = 5;
	var exp = iat + minutesToAdd * 60;

	// Defining our token parts
	var header = {
		"alg": "HS256",
		"typ": "JWT"
	};
	
	var data = {
		"iss":  clientId,
		"exp": exp,
		"iat": iat,
	};
	
	var stringifiedHeader = CryptoJS.enc.Utf8.parse(JSON.stringify(header));
	var encodedHeader = base64url(stringifiedHeader);

	var stringifiedData = CryptoJS.enc.Utf8.parse(JSON.stringify(data));
	var encodedData = base64url(stringifiedData);

	var headerAndData = encodedHeader + "." + encodedData;

	var signature = CryptoJS.HmacSHA256(headerAndData, CryptoJS.enc.Base64.parse(clientSecret));
    var signature = base64url(signature);

	var jwt = headerAndData + "." + signature;
	console.log("jwt token created: " + jwt);
	return jwt;
}

//export default function jwt(){create_client_jwt(g_clientId, g_clientSecret)};