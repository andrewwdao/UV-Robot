
// function close_window() {
// 	if (confirm("Close Window?")) {
// 		window.close();
// 	}
//   }

// $(document).ready(function(){
// 	$("#cancel").on("click", function() {
// 		$( "#connect" ).slideUp( "fast", function() {});
// 		$( "#connect_manual" ).slideUp( "fast", function() {});
// 		$( "#wifi" ).slideDown( "fast", function() {});
// 	});

// 	$("#ok-credits").on("click", function() {
// 		$( "#credits" ).slideUp( "fast", function() {});
// 		$( "#app" ).slideDown( "fast", function() {});
		
// 	});
	
// 	$("#acredits").on("click", function() {
// 		$( "#app" ).slideUp( "fast", function() {});
// 		$( "#credits" ).slideDown( "fast", function() {});
// 	});
// })

document.addEventListener("keydown", keyPressed, false);

var socket = io();
socket.on('connect', () => {
    socket.emit('hello', {data: "User connected"});
    console.log("Connected");
    console.log(socket);
})

socket.on('my response', () => {
    console.log("Response from server");
});

function keyPressed(e) {
    var keyCode = e.keyCode;
    if(keyCode==87) {
        console.log("W");
        socket.emit('hello')
    } else if (keyCode==65) {
        console.log("A");
    } else if (keyCode==68) {
        console.log("D");
    } else if (keyCode==83) {
        console.log("S");
    }
}