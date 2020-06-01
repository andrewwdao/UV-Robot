
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
// document.addEventListener("keypress", keyPressed, false);
document.addEventListener("keydown", keyIsPressing, false);
document.addEventListener("keyup", keyReleased, false);

const K_SIGNAL = 0, K_ID = 1;
const keyMap = {
    87: ['UP', 'w'],                             // W
    65: ['LEFT', 'a'],                           // A
    68: ['RIGHT', 'd'],                          // D
    83: ['DOWN', 's'],                           // S
    72: ['LHAND_UP', 'h'],                       // H
    74: ['LHAND_DOWN', 'j'],                     // J
    75: ['RHAND_UP', 'k'],                       // K
    76: ['RHAND_DOWN', 'l'],                     // L
    81: ['SPEED', 'q',],                         // Q
    32: ['TOGGLE', 'space',],                    // Space
};

var socket = io();

socket.on('connect', () => {
    console.log("Server connected");
});

lastTime = new Date().getTime();
lightOn = false;
lightPressedTime = 0;

function keyIsPressing(e) {
    if (document.getElementById("app-inner")) {
        var pressedKey = keyMap[e.keyCode];
        if (pressedKey) {
            document.getElementById(pressedKey[K_ID]).classList.add("pressed");
            // console.log(pressedKey[K_ID]+ " pressing");

            var curTime = new Date().getTime();

            if (curTime - lastTime < 100) // ms
                return;
    
            lastTime = curTime;
        
            if (pressedKey[K_SIGNAL] === 'TOGGLE') {
                var duration = curTime - lightPressedTime;
                if (lightPressedTime === 0) {
                    lightPressedTime = new Date().getTime();
                    console.log("JUST GET HERE ONCE");
                } else if ((duration >= 1000 && duration <= 1500 && !lightOn) ||
                            (duration < 500 && lightOn)) {
                    lightOn = !lightOn;
                    lightPressedTime = 1600;
                    console.log("LIGHT");
                    if (lightOn) {
                        document.getElementById("space").classList.add("active");
                    } else {
                        document.getElementById("space").classList.remove("active");
                    }
                } else {
                    return;
                }
            }

            socket.emit('holding', pressedKey[K_SIGNAL]);
        }
    }
}

function keyReleased(e) {
    if (document.getElementById("app-inner")) {
        var releasedKey = keyMap[e.keyCode];
        if (releasedKey) {
            if (releasedKey[K_SIGNAL] === 'TOGGLE') {
                lightPressedTime = 0;
            }

            document.getElementById(releasedKey[K_ID]).classList.remove("pressed");
            console.log(releasedKey[K_ID] + " released");
            socket.emit('released', releasedKey[K_SIGNAL] + "R")
        }
    }
}

// function keyPressed(e) {
//     if (document.getElementById("app-inner")) {
//         var pressedKey = keyMap[e.keyCode];
//         if (pressedKey) {
//             if (!document.getElementById(pressedKey[K_ID]).classList.contains('pressed')) {
//                 document.getElementById(pressedKey[K_ID]).classList.add("pressed");
//                 console.log(pressedKey[K_ID]+ " pressed");
//                 socket.emit('pressed', pressedKey[K_SIGNAL] + "P");
//             }
//         }
//     }
// }
