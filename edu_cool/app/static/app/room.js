console.log('jsslinked frfrfrrr')


let ws = connect()


function connect(){

	socket = new WebSocket(
		'ws://' + 
		window.location.host + '/ws/chat/'+ 
		window.location.pathname.split('/')[2] + '/'
	)

	socket.onopen = ()=>{
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