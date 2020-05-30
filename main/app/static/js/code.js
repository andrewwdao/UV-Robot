
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

lastTime = new Date().getTime();

function keyPressed(e) {
    if (document.getElementById("app-inner")) {
        var curTime = new Date().getTime();

        if (curTime - lastTime < 100) // ms
            return;
    
        lastTime = curTime;
    
        var keyCode = e.keyCode;
        switch (keyCode) {
            case 87: //W
                // console.log("W");
                socket.emit('key pressed', 'UP');
                break;
            case 65: //A
                socket.emit('key pressed', 'LEFT');
                break;
            case 68: //D
                socket.emit('key pressed', 'RIGHT');
                break;
            case 83: //S
                socket.emit('key pressed', 'DOWN');
                break;
            
            case 72: //H
                socket.emit('key pressed', 'LHAND_UP');
                break;
            case 74: //J
                socket.emit('key pressed', 'LHAND_DOWN');
                break;
            case 75: //K
                socket.emit('key pressed', 'RHAND_UP');
                break;
            case 76: //L
                socket.emit('key pressed', 'RHAND_DOWN');
                break;

            case 49: //1
                socket.emit('key pressed', 'LOW_SPEED');
                break;
            case 50: //2
                socket.emit('key pressed', 'HIGH_SPEED');
                break;
        }
    }
}