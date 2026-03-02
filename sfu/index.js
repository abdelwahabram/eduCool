console.log('server running frfrfrfrfrfr')

import axios from 'axios';

import { secrets } from "docker-secret";

import * as mediasoup from "mediasoup";

import os from 'node:os';

// import os;

let ws;

let routers = new Map()

let peersInRoom = new Map()

let sendTransport = new Map()

let producers = new Map();

let recvTransport = new Map()

let consumers = new Map()

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


function what_is_my_ip(){

	/* return the container ip if run inside a container ,otherwise the host ip */

	const interfaces = os.networkInterfaces();

	// console.log(interfaces)

	for(const i of Object.values(interfaces)){
		if (i['internal'] === false && i['family'] === 'IPv4'){
			return i['address']
		}
	}

}


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
			announcedAddress: process.env.ANNOUNCEDIP || what_is_my_ip(),
			port     : 20000
		// set public ip for production, or private for dev

		// we can't use service name as it will be sent to the client as a literal string
		// during ice exchange to allow p2p communication behind nat, we need to send an ip

		// also we can't use "127.0.0.1" , as some browsers(ff) 
		// don't listen to it during ice exchange
		},

		{
			protocol : 'tcp',
			ip       : '0.0.0.0',
			announcedAddress: process.env.ANNOUNCEDIP || what_is_my_ip(),
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

		let transport = sendTransport.get(messageJson['content']['transportId'])

		connectTransport(messageJson, transport)

	}else if(messageJson['type'] === 'transport-produce'){

		produce(messageJson)

	}else if(messageJson['type'] === 'recv-transport-request'){

		createRecvTransport(messageJson)

	}else if(messageJson['type'] === 'recv-transport-connect'){

		let transport = recvTransport.get(messageJson['content']['transportId'])

		connectTransport(messageJson, transport)

	}else if(messageJson['type'] === 'canConsume?'){

		consume(messageJson)
	}else if(messageJson['type'] === 'resume'){
		resume(messageJson['content'])
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

	let router = await worker.createRouter({mediaCodecs,})

	peersInRoom.set(room, new Set())

	routers.set(room, router)

	return router

}


async function createTransport(room){

	let router = await getRouter(room)

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

	return transport

}


async function createSendTransport(content){

	let transport = await createTransport(content['room'])

	let remoteChannel = content['sender_channel']

	sendTransport.set(transport.id, transport)

	let transportData = {
		id: transport.id,
		iceParameters: transport.iceParameters,
		iceCandidates: transport.iceCandidates,
		dtlsParameters: transport.dtlsParameters,
		sctpParameters: transport.sctpParameters
	}

	sendMessage('send-transport-created', transportData, remoteChannel)

}


async function connectTransport(message, transport){

	let remoteChannel = message['sender_channel']

	await transport.connect(message['content'])

	let type

	if(message['type'] === 'transport-connect'){

		type = 'connect-callback'

	}else{

		type = 'recv-connect-callback'
	}

	sendMessage(type, '', remoteChannel)

}


async function produce(message){

	let remoteChannel = message['sender_channel']

	let transport = sendTransport.get(message['content']['transportId'])

	// console.log('producing', message['content'])
	
	let producer = await transport.produce(message['content'])

	// producers.set(transport.id, producer)

	saveProducer(transport.id, producer)

	sendMessage('produce-callback', {id: producer.id}, remoteChannel)

	notifyPeers(transport.id, producer.kind, message['room'])

}


function saveProducer(transportId, producer){

	if(!producers.has(transportId)){
		producers.set(transportId, {'audio': null, 'video': null})
	}

	producers.get(transportId)[producer.kind] = producer
}


function notifyPeers(transportId, kind, room){

	console.log(peersInRoom.get(room))
	for( let peer of peersInRoom.get(room)){
		sendMessage('new-peer', {id: transportId, kind: kind}, peer)
	}

}


async function createRecvTransport(message){

	let transport = await createTransport(message['room'])

	recvTransport.set(transport.id, transport)
	// save the obj by id to connect with client transport and create consumer

	let remoteChannel = message['sender_channel']

	let transportData = {

		id: transport.id,
		iceParameters: transport.iceParameters,
		iceCandidates: transport.iceCandidates,
		dtlsParameters: transport.dtlsParameters, 
		sendTransportId: message['content']['id'],
		kind: message['content']['kind']
	}

	sendMessage('recv-transport-created', transportData, remoteChannel)
}


async function consume(message){

	let remoteChannel = message['sender_channel']

	let sendTransportId = message['content']['sendTransportId']

	let kind = message['content']['kind']

	let producer = producers.get(sendTransportId)[kind]
	
	console.log('consuming', producer.kind, producer.id)
	let router = await getRouter(message['room'])

	let consumerOptions = {producerId: producer.id, rtpCapabilities: message['content']['rtpc'], paused: true}

	if(!router.canConsume(consumerOptions)){

		console.log(remoteChannel, 'can not consume media from ', sendTransportId )

		sendMessage('device can not consume produced media', '', remoteChannel)

		return

	}

	let transport = recvTransport.get(message['content']['recvTransportId'])

	let consumer = await transport.consume(consumerOptions)

	let clientConsumerOptions = {
		id: consumer.id,
		producerId: consumer.producerId,
		kind: consumer.kind,
		rtpParameters: consumer.rtpParameters,
		recvTransportId: message['content']['recvTransportId']
	}

	consumers.set(consumer.id, consumer)

	sendMessage('consume', clientConsumerOptions, remoteChannel)
}

async function resume(consumerId){

	console.log('resuming')

	let consumer = consumers.get(consumerId)

	console.log(consumer.id)

	await consumer.resume()
}