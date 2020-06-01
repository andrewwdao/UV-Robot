
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
    87: ['UP', 'w', false],                             // W
    65: ['LEFT', 'a', false],                           // A
    68: ['RIGHT', 'd', false],                          // D
    83: ['DOWN', 's', false],                           // S
    72: ['LHAND_UP', 'h', false],                       // H
    74: ['LHAND_DOWN', 'j', false],                     // J
    75: ['RHAND_UP', 'k', false],                       // K
    76: ['RHAND_DOWN', 'l', false],                     // L
    81: ['SPEED', 'q',, false],                         // Q
    32: ['TOGGLE', 'space',, false],                    // Space
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
            var curTime = new Date().getTime();

            if (curTime - lastTime < 100) // ms
                return;
    
            lastTime = curTime;
        
            document.getElementById(pressedKey[K_ID]).classList.add("pressed");
            // console.log(pressedKey[K_ID]+ " pressing");

            if (pressedKey[K_SIGNAL] === 'TOGGLE') {
                if (lightOn) {
                    toggleLight();
                    lightPressedTime = 1600;
                } else if (lightPressedTime === 0 && !lightOn) {
                    lightPressedTime = new Date().getTime();
                } else if (curTime - lightPressedTime > 1000 && !lightOn && curTime - lightPressedTime < 1500) {
                    toggleLight();
                    lightPressedTime = 1600;
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

function toggleLight() {
    lightOn = !lightOn;
    console.log("LIGHT");

    if (lightOn) {
        document.getElementById("space").classList.add("active");
    } else {
        document.getElementById("space").classList.remove("active");
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
