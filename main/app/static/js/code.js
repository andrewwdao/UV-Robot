
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
    console.log("Server connected");
});

function keyPressed(e) {
    var keyCode = e.keyCode;
    if(keyCode==87) { //W
        console.log("W");
        socket.emit('key pressed', 'UP');
    } else if (keyCode==65) { //A
        console.log("A");
        socket.emit('key pressed', 'LEFT');
    } else if (keyCode==83) { //S
        console.log("S");
        socket.emit('key pressed', 'DOWN');
    } else if (keyCode==68) { //D
        console.log("D");
        socket.emit('key pressed', 'RIGHT');
    }
}