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

		let id = messageJson['content'][id]

		savedProduceCallback({id})

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

	createDev(content).then(()=>{requestSendTransport()})
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

async function createSendTransport(content){

	try{

		sendTransport = await device.createSendTransport(content)

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