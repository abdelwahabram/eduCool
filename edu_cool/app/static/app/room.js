console.log('jsslinked frfrfrrr')

import * as mediasoupClient from "mediasoup-client";

const mediaSpecs = {
  audio: true,
  video: { facingMode: "user", width: 250, height: 200 },
};

let audioProducerOptions = {};
let videoProducerOptions = {};


let device;


let ws = connect()

let sendTransport;

let savedConnectCallback;

let savedProduceCallback;

let recvTranportCallBacks = new Map();

let recvTransports = new Map();

let connectedReceiver = new Map();

let senders = new Set()

let producedKinds = new Map()


function connect(){

	socket = new WebSocket(
		'ws://' + 
		window.location.host + '/ws/chat/'+ 
		window.location.pathname.split('/')[2] + '/'
	)

	socket.onopen = ()=>{
		console.log('skibidi connection')

		getUserMedia()

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


function handleNewMessage(event){

	console.log('new msg')

	let messageJson = JSON.parse(event.data)['message']

	let type = messageJson['type']

	console.log(type)

	if (type === "RTPC"){
		
		handleRTPC(messageJson['content'])

	}else if (type === 'send-transport-created'){

		createSendTransport(messageJson['content'])

	}else if(type === 'connect-callback'){

		savedConnectCallback()

	}else if(type === 'produce-callback'){

		let id = messageJson['content']['id']

		savedProduceCallback({id})

	}else if(type === 'new-peer'){

		requestRecvTransport(messageJson['content'])

	}else if(type === 'recv-transport-created'){

		createRecvTransport(messageJson['content'])

	}else if(type === 'recv-connect-callback'){

		let recvTransportId = messageJson['content']

		callback = recvTranportCallBacks.get(recvTransportId)

		callback()

	}else if(type === 'consume'){

		consume(messageJson['content'])

	}else if(type === 'peers-list'){

		console.log(messageJson)

		addPeers(messageJson['content'])
	}
}


function sendMessage(type, content, remoteChannel = ''){

	console.log('sending: ...', type)

    let jsonMessage = JSON.stringify({'message':
        {type: type, content:content, receiver_channel: remoteChannel}
    })

    ws.send(jsonMessage)

};


function getUserMedia(){

	navigator.mediaDevices.getUserMedia(mediaSpecs).then(handleUserStream).catch((error)=>{
		console.log('error capturing user media: ', error)
	})

}

function handleUserStream(stream){

	console.log('%captured local stream successfully%')

	const localVideoElm = document.querySelector('.local-video').children[1]
	// .getElementsByTagName('video')

	localVideoElm.srcObject = stream

	audioProducerOptions['track'] = stream.getAudioTracks()[0]

	videoProducerOptions['track'] = stream.getVideoTracks()[0]

	start()

}

function start(){

	sendMessage('router-rtp-request', '')
	
}


function handleRTPC(content){

	createDev(content).then(()=>{
		requestSendTransport()
		requestPreviousPeers()
	})
}


async function createDev(rtpc){

	console.log(" creating dev")

	try{

		device = await mediasoupClient.Device.factory();

	}catch (error){

		if (error.name === 'UnsupportedError')
			console.warn('browser not supported');
	}

	await device.load({ routerRtpCapabilities:rtpc });

}


function requestSendTransport(){

	sendMessage('send-transport-request', '')
}

function requestPreviousPeers(){
	sendMessage('peers-request', '')
}

function createSendTransport(content){

	try{

		sendTransport = device.createSendTransport(content)

	}catch(error){
		console.log(error)
	}
	
	sendTransport.on("connect", async ({ dtlsParameters }, callback, errback) =>{
		try{

			sendMessage("transport-connect", {transportId: sendTransport.id, dtlsParameters:dtlsParameters})

			savedConnectCallback = callback
			// save this function to be called later once the server have been notified, and replied with 'connect-callback'

		}catch(error){
			errback(error)
		}
	})

	sendTransport.on("produce", async (parameters, callback, errback) =>{
		try{

			let produceParameters = {
				transportId: sendTransport.id, 
				kind: parameters.kind, 
				rtpParameters: parameters.rtpParameters, 
				appData: parameters.appData
			}

			sendMessage('transport-produce', produceParameters)

			savedProduceCallback = callback
			// save this function until we receive 'produce-callback' with the id

		}catch(error){
			errback(error)
		}
	})

	sendTransport.on('connectionstatechange', (connectionState)=>{
		console.log('state', connectionState)
	})


	sendTransport.on('icecandidateerror', (e)=>{
		console.log('ice error', e)
	})

	produce()

}

async function produce(){

	vProducer = await sendTransport.produce(videoProducerOptions)
	
	aProducer = await sendTransport.produce(audioProducerOptions)


	vProducer.on("transportclose", () =>{
		console.log("transport closed so video producer closed");
	});

	vProducer.on("trackended", () =>{
		console.log("video track ended");
	});


	aProducer.on("transportclose", () =>{
		console.log("transport closed so audio producer closed");
	});

	aProducer.on("trackended", () =>{
		console.log("audio track ended");
	});

}


function requestRecvTransport(message){

	let id = message['id']

	if( id === sendTransport.id){
		return
	}

	if(senders.has(id)){

		if (producedKinds.get(id) === null){
			producedKinds.set(id, message['kind'])
		}else if(producedKinds.get(id) !== message['kind']){
			producedKinds.set(id, 'both')
		}
		// canConsume(connectedReceiver.get(id), id, message['kind'])
		return
	}

	senders.add(id)

	producedKinds.set(id, message['kind'])
	sendMessage('recv-transport-request', message)
}


function createRecvTransport(message){

	let transport = device.createRecvTransport(message)

	transport.on("connect", ({ dtlsParameters }, callback, errback) =>{

		try{

			sendMessage('recv-transport-connect', {transportId: transport.id, dtlsParameters: dtlsParameters})

			recvTranportCallBacks.set(transport.id, callback)

		}catch(error){

			errback(error)
		}
	})

	recvTransports.set(transport.id, transport)

	connectedReceiver.set(message['sendTransportId'], transport.id)
	console.log('created', message['kind'])
	canConsume(transport.id, message['sendTransportId'], message['kind'])

}


function canConsume(recvTransportId, sendTransportId, kind){
	
	// the receiver consumes media from the producer of this sendTransport
	let content = {
		rtpc: device.rtpCapabilities,
		recvTransportId: recvTransportId,
		sendTransportId: sendTransportId,
		kind: producedKinds.get(sendTransportId)
	}

	// console.log(content)
	sendMessage('canConsume?', content)

	producedKinds.set(sendTransportId, null)
	
}


async function consume(message){

	// console.log(message)

	let recvTransportId = message['recvTransportId']

	let transport = recvTransports.get(recvTransportId)

	let consumer = await transport.consume(message)

	let username = message['username']

	let elements = createWrapper(recvTransportId, username)

	const { track } = consumer;

	// if (message['kind'] === 'video'){
	// 	elements[0].srcObject = track
	// }

	console.log(track)

	console.log(message['kind'])
	console.log(elements[message['kind']])
	elements[message['kind']].srcObject = new MediaStream([ track ]);

	sendMessage('resume', consumer.id)


}

function createWrapper(recvTransportId, username = ''){

	console.log('creating elms')

	if (document.getElementById(recvTransportId) !== null){
		let audio = document.getElementById('audio-' + recvTransportId)
		let video = document.getElementById('video-' + recvTransportId)

		return {'video': video, 'audio': audio}
	}

	let user = document.createElement('h2')

	user.innerHTML = username

	let audio = document.createElement('audio')
	audio.id = 'audio-' + recvTransportId
	audio.autoplay = true

	let video = document.createElement('video')
	video.id = 'video-'+ recvTransportId
	video.autoplay= true
	video.playsinline = true

	let wrapper = document.createElement('div')

	wrapper.id = recvTransportId

	wrapper.append(user, video, audio)

	let container = document.getElementsByClassName('videos-container')[0]

	container.append(wrapper)

	return {'video': video, 'audio': audio}
}

function addPeers(peersList){
	console.log('p',peersList)
	console.log('t', typeof(peersList))

	for(let transportId of peersList.values()){

		// if (senders.has(transportId)){
		// 	continue
		// }

		requestRecvTransport({id: transportId, kind: 'video'})
		requestRecvTransport({id: transportId, kind: 'audio'})
	}


}