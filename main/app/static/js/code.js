
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
document.addEventListener("keyup", keyReleased, false);

const K_SIGNAL = 0, K_CLASS = 1;
const keyMap = {
    87: ['UP', 'w'],           // W
    65: ['LEFT', 'a'],         // A
    68: ['RIGHT', 'd'],        // D
    83: ['DOWN', 's'],         // S
    72: ['LHAND_UP', 'h'],     // H
    74: ['LHAND_DOWN', 'j'],   // J
    75: ['RHAND_UP', 'k'],     // K
    76: ['RHAND_DOWN', 'l'],   // L
    49: ['K1', 'k1'],          // 1
    50: ['K2', 'k2'],          // 2
    32: ['SPACE', 'space'],    // Space
};

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
    
        var pressedKey = keyMap[e.keyCode];
        if (pressedKey) {
            if (!document.getElementById(pressedKey[K_CLASS]).classList.contains('pressed')) {
                document.getElementById(pressedKey[K_CLASS]).classList.add("pressed");
                console.log(pressedKey[K_CLASS]);
                socket.emit('key pressed', pressedKey[K_SIGNAL]);
            }
        }
    }
}

function keyReleased(e) {
    var pressedKey = keyMap[e.keyCode];
    if (pressedKey) {
        document.getElementById(pressedKey[K_CLASS]).classList.remove("pressed");
        console.log(pressedKey[K_CLASS] + " released");
        socket.emit('key released', pressedKey[K_SIGNAL] + " released")
    }
}
