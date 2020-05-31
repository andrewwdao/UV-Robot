
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

// ref: https://www.w3schools.com/jsref/dom_obj_event.asp
document.addEventListener("keypress", keyPressed, false);
// document.addEventListener("keydown", keyIsPressing, false);
document.addEventListener("keyup", keyReleased, false);

const K_SIGNAL = 0, K_ID = 1;
const keyMap = {
    87: ['UP', 'w'],           // W
    65: ['LEFT', 'a'],         // A
    68: ['RIGHT', 'd'],        // D
    83: ['DOWN', 's'],         // S
    72: ['LHAND_UP', 'h'],     // H
    74: ['LHAND_DOWN', 'j'],   // J
    75: ['RHAND_UP', 'k'],     // K
    76: ['RHAND_DOWN', 'l'],   // L
    49: ['HIGH_SPEED', 'k1'],          // 1
    50: ['LOW_SPEED', 'k2'],          // 2
    32: ['TOGGLE', 'space'],    // Space
};

var socket = io();

socket.on('connect', () => {
    console.log("Server connected");
});

lastTime = new Date().getTime();

function keyPressed(e) {
    if (document.getElementById("app-inner")) {
        var pressedKey = keyMap[e.keyCode];
        if (pressedKey) {
            if (!document.getElementById(pressedKey[K_ID]).classList.contains('pressed')) {
                document.getElementById(pressedKey[K_ID]).classList.add("pressed");
                console.log(pressedKey[K_ID]+ " pressed");
                socket.emit('pressed', pressedKey[K_SIGNAL] + "P");
            }
        }
    }
}

function keyIsPressing(e) {
    if (document.getElementById("app-inner")) {
        var curTime = new Date().getTime();

        if (curTime - lastTime < 100) // ms
            return;
    
        lastTime = curTime;
    
        var pressedKey = keyMap[e.keyCode];
        if (pressedKey) {
            document.getElementById(pressedKey[K_ID]).classList.add("pressed");
            socket.emit('holding', pressedKey[K_SIGNAL]);
        }
    }
}

function keyReleased(e) {
    if (document.getElementById("app-inner")) {
        var pressedKey = keyMap[e.keyCode];
        if (pressedKey) {
            document.getElementById(pressedKey[K_ID]).classList.remove("pressed");
            console.log(pressedKey[K_ID] + " released");
            socket.emit('released', pressedKey[K_SIGNAL] + "R")
        }
    }
}
