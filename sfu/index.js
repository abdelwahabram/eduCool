console.log('server running frfrfrfrfrfr')

// send get req to login
// extract the csrf token
// extract the creds from the docker secret
// send post req to login
// extract the cookie from the response obj
// open ws connection with cookie included


import axios from 'axios';

import { secrets } from "docker-secret";


function parseCookie(header){

	let keyValue = header.split(';')[0] + ";"

	return keyValue

	// let key = keyValue[0]
	// let value = keyValue[1]

	// return {key: key, value: value}

}

console.log("ss: ", secrets.server_cred_username)

axios.post('http://django:8000/login/', 
	{username: secrets.server_cred_username, password: secrets.server_cred_pass}).then(function (response) {
		// handle success
		console.log(response.headers['set-cookie']);
		console.log(response.data);

		let cookies = ''

		for (let cookie of response.headers['set-cookie']){

			let parsedCookie = parseCookie(cookie)

			cookies = cookies + parsedCookie

			// cookies[parsedCookie['key']] = parsedCookie['value']


		}

		console.log(cookies)
		return cookies

	}).then(function(cookies){

		console.log(cookies)

		const chatSocket = new WebSocket(
			'ws://' + 'django:8000' + '/ws/chat/',

			{'headers': {
            'Cookie': cookies
				}
         }
      )

		chatSocket.onopen = function(e){
			console.log('skibidi connection')
		}

  })


