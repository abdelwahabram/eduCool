console.log('server running frfrfrfrfrfr')

import axios from 'axios';

import { secrets } from "docker-secret";

import * as mediasoup from "mediasoup";


axios.post('http://django:8000/login/', {username: secrets.server_cred_username, 
	password: secrets.server_cred_pass}).then(function (response) {

		let cookies = ''

		for (let cookie of response.headers['set-cookie']){

			let parsedCookie = parseCookie(cookie)

			cookies = cookies + parsedCookie

		}

		return cookies

	}).then((cookies)=>{let ws = connect(cookies)})


let worker = await createWorker()


function connect (cookies){

	const socket = new WebSocket(
		'ws://' + 'django:8000' + '/ws/chat/',
		{'headers': {
		'Cookie': cookies}
	})


	socket.onopen = function(e){
		console.log('skibidi connection')
	}


	socket.onmessage = handleNewMessage


	socket.onclose = (event)=>{
		console.log('socket closed')
		console.log(event.reason)
	}

	socket.onerror = (event)=>{
		console.log('socket err')
		console.log(event)
	}

	return socket

}


async function createWorker(){

	const worker = await mediasoup.createWorker()

	worker.on("died", (error) =>{
		console.error("mediasoup worker died!: %o", error);
	});

}


function parseCookie(header){

	let keyValue = header.split(';')[0] + ";"

	return keyValue

}


let handleNewMessage = (event)=>{
	console.log('new msg')
}


function sendMessage(type, content, remoteChannel = ''){

	console.log('sending: ...', type)

    let jsonMessage = JSON.stringify({'message':
        {type: type, content:content, receiver_channel: remoteChannel}
    })

    ws.send(jsonMessage)

};


