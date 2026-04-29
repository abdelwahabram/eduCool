console.log('jsslinked frfrfrrr')

import * as mediasoupClient from "mediasoup-client";

const mediaSpecs = {
  audio: true,
  video: { facingMode: "user", width: { min: 1024, ideal: 1280, max: 1920 }, height: { min: 576, ideal: 720, max: 1080 } , resizeMode: "crop-and-scale"},
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

		addPeers(messageJson['content'])

	}else if(type === 'sendTransportClosed'){
		removePeer(messageJson)
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
		// requestPreviousPeers()
		/*
			if we started sending requestRecvTransport() before creating a sendTransport we can't compare the id of the sendTransport
		*/
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

		requestPreviousPeers()

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

	if(sendTransport === null){
		return
	}

	let id = message['id']

	if( id === sendTransport.id){
		return
	}

	if(senders.has(id)){

		producedKinds.get(id).add(message['kind'])

		return
	}

	senders.add(id)

	producedKinds.set(id, new Set())

	producedKinds.get(id).add(message['kind'])

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

	let kind = producedKinds.get(message['sendTransportId'])

	for(let kind of producedKinds.get(message['sendTransportId'])){
		
		canConsume(transport.id, message['sendTransportId'], kind)

		producedKinds.get(message['sendTransportId']).delete(kind)
	}

}


function canConsume(recvTransportId, sendTransportId, kind){
	
	// the receiver consumes media from the producer of this sendTransport
	let content = {
		rtpc: device.rtpCapabilities,
		recvTransportId: recvTransportId,
		sendTransportId: sendTransportId,
		kind: kind
	}

	sendMessage('canConsume?', content)
	
}


async function consume(message){

	let recvTransportId = message['recvTransportId']

	let transport = recvTransports.get(recvTransportId)

	let consumer = await transport.consume(message)

	let username = message['username']

	let elements = createWrapper(recvTransportId, username)

	const { track } = consumer;

	elements[message['kind']].srcObject = new MediaStream([ track ]);

	sendMessage('resume', consumer.id)

}


function createWrapper(recvTransportId, username = ''){

	console.log('creating elms')

	if (document.getElementById(recvTransportId) !== null){
		console.log('already exists')
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

	for(let transportId of peersList.values()){

		requestRecvTransport({id: transportId, kind: 'video'})

		requestRecvTransport({id: transportId, kind: 'audio'})
	}

}


function removePeer(message){

	let sendTransportId = message['content']

	let recvTransportId = connectedReceiver.get(sendTransportId)

	if(recvTransportId === null){
		return
	}

	recvTransports.get(recvTransportId).close()

	let wrapper = document.getElementById(recvTransportId)

	wrapper.remove()

	removeRecvTransportOf(sendTransportId)

}


function removeRecvTransportOf(sendTransportId){
	
	let recvTransportId = connectedReceiver.get(sendTransportId)

	recvTranportCallBacks.delete(recvTransportId)

	recvTransports.delete(recvTransportId)

	senders.delete(sendTransportId)

	producedKinds.delete(sendTransportId)

	connectedReceiver.delete(sendTransportId)
}