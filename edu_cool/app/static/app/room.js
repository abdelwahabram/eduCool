console.log('jsslinked frfrfrrr')


const mediaSpecs = {
  audio: true,
  video: { facingMode: "user", width: 250, height: 200 },
};

let audioProducerOptions = {};
let videoProducerOptions = {};


let ws = connect()


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