console.log('server running frfrfrfrfrfr')

import axios from 'axios';

import { secrets } from "docker-secret";

import * as mediasoup from "mediasoup";

let ws;

let routers = new Map()

let peersInRoom = new Map()

let transportOfPeer = new Map()

let mediaCodecs = [
	{
		kind: "video",
		mimeType: "video/H264",

		/*
			// h264 over vp9 or 8 for video conference
			// as the higher the compression rate(in vp), the longer the encoding time=> higher latency
			// but if we need to pay a royalty fee, then go for vp8,9 but this is up to the browser or the os if i'm not mistaken
			// I hope I'm not. is this serious?! what's the worst thing that can happen? they're gonna sue me???
			"your honor, it's just a side project"
		*/

		clockRate: 90000,
		parameters:{
			"profile-level-id": "42e01f",
			// 42e0 represents h264 baseline profile, it's simple, require less processing and it has low latency which is good for video conference
			"packetization-mode": 1,
			"level-asymmetry-allowed": 1
		}
	},

	{
		kind: "audio",
		mimeType: "audio/opus",
		clockRate: 48000,
		channels: 2

	}
]


axios.post('http://django:8000/login/', {username: secrets.server_cred_username, 
	password: secrets.server_cred_pass}).then(function (response) {

		let cookies = ''

		for (let cookie of response.headers['set-cookie']){

			let parsedCookie = parseCookie(cookie)

			cookies = cookies + parsedCookie

		}

		return cookies

	}).then((cookies)=>{ws = connect(cookies)})


let worker = await createWorker()

let webRtcServer = await createWebRtcServer()


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

	return worker

}


async function createWebRtcServer(){

	const wrtcServer = await worker.createWebRtcServer({listenInfos:[
      {
        protocol : 'udp',
        ip       : '0.0.0.0',
        announcedAddress: 'sfu',
        port     : 20000
      },
      {
        protocol : 'tcp',
        ip       : '0.0.0.0',
        announcedAddress: 'sfu',
        port     : 20000
      }
    ]})

	return wrtcServer
}


function parseCookie(header){

	let keyValue = header.split(';')[0] + ";"

	return keyValue

}


let handleNewMessage = (event)=>{
	console.log('new msg')

	let messageJson = JSON.parse(event.data)['message']

	console.log(messageJson['type'])

	if (messageJson['type'] === 'router-rtp-request'){

		handleRtpRequest(messageJson)

	}else if(messageJson['type'] === 'send-transport-request'){

		createSendTransport(messageJson)

	}else if(messageJson['type'] === 'transport-connect'){

		sendTransportConnect(messageJson)

	}else if(messageJson['type'] === 'transport-produce'){

		produce(messageJson)

	}
}


function sendMessage(type, content, remoteChannel = ''){

	console.log('sending: ...', type)

    let jsonMessage = JSON.stringify({'message':
        {type: type, content:content, receiver_channel: remoteChannel}
    })

    ws.send(jsonMessage)

};


async function handleRtpRequest(message){

	let remoteChannel = message['sender_channel']

	let router = await getRouter(message['room'])

	peersInRoom.get(message['room']).add(remoteChannel)

	sendMessage('RTPC', router.rtpCapabilities, remoteChannel)

}


async function getRouter(room){

	if (routers.has(room)){

		return routers.get(room)
	}

	let router = worker.createRouter({mediaCodecs,})

	peersInRoom.set(room, new Set())

	routers.set(room, router)

	return router

}


async function createSendTransport(content){

	let router = await getRouter(content['room'])

	let transport = await router.createWebRtcTransport({webRtcServer : webRtcServer})

	transport.on('icestatechange', (iceState)=>{
		if(iceState === "disconnected"){
			console.log("ice state: disconnected, transport will be closed")
			transport.close()
		}
	})

	transport.on('dtlsstatechange', (dtlsState)=>{

		if(dtlsState === "closed"){
			console.log("dtls is closed, transport will be closed")
			transport.close()
		}
	})

	let remoteChannel = content['sender_channel']

	transportOfPeer.set(remoteChannel, transport)

	let transportData = {
		id: transport.id,
		iceParameters: transport.iceParameters,
		iceCandidates: transport.iceCandidates,
		dtlsParameters: transport.dtlsParameters,
		sctpParameters: transport.sctpParameters
	}

	sendMessage('send-transport-created', transportData, remoteChannel)

}


async function sendTransportConnect(message){

	let remoteChannel = message['sender_channel']

	let transport = transportOfPeer.get(remoteChannel)

	await transport.connect(message['content'])

	sendMessage('connect-callback', '', remoteChannel)

}


async function produce(message){

	let remoteChannel = message['sender_channel']

	let transport = transportOfPeer.get(remoteChannel)

	let producer = await transport.produce(message['content'])

	sendMessage('produce-callback', {id: producer.id}, remoteChannel)
}