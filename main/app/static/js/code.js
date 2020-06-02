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
    72: ['L_UP', 'h', false],                           // H
    74: ['L_DOWN', 'j', false],                         // J
    75: ['R_UP', 'k', false],                           // K
    76: ['R_DOWN', 'l', false],                         // L
    81: ['SPEED', 'q',, false],                         // Q
    32: ['TOGGLE', 'space',, false],                    // Space
};

var socket = io();
lastTime = new Date().getTime();
lightOn = false;
lightPressedTime = 0;

// ----------------------- client signal listener --------------------------
socket.on('connect', () => {
    console.log("Server connected");
});

socket.on('light', (status) => {
    lightOn = status;

    lightToggler = document.getElementById("space");
    if (lightOn === 'ON') {
        console.log("light on");
        lightToggler.classList.add("active");
    } else {
        console.log("light off");
        lightToggler.classList.remove("active");
    }

    lightToggler.classList.remove("pressed");
});

socket.on('speed', (status) => {
    speedState = status;

    speedToggler = document.getElementById("q");
    if (speedState === 'HIGH') {
        console.log("high speed mode");
        speedToggler.classList.add("active");
    } else {
        console.log("low speed mode");
        speedToggler.classList.remove("active");
    }

    speedToggler.classList.remove("pressed");
});

// ----------------------- client signal emitter ----------------------------
function keyIsPressing(e) {
    var pressedKey = keyMap[e.keyCode];
    if (pressedKey) {
        var curTime = new Date().getTime();

        if (curTime - lastTime < 100) // ms
            return;

        lastTime = curTime;

        // ----------------------- toggle light function ------------------------
        if (pressedKey[K_SIGNAL] === 'TOGGLE') {
            if ((lightOn && lightPressedTime === 0) ||
                (curTime - lightPressedTime > 1000 && !lightOn && curTime - lightPressedTime < 1500)) {
                socket.emit('light');
                lightPressedTime = 1600;
            } else if (lightPressedTime === 0 && !lightOn) {
                lightPressedTime = new Date().getTime();
                document.getElementById(pressedKey[K_ID]).classList.add("pressed");
            }
            return;
        }
        // ----------------------- toggle speed function ------------------------
        if (pressedKey[K_SIGNAL] === 'SPEED') {
            socket.emit('speed');
        } else {
            socket.emit('pressed', pressedKey[K_SIGNAL]);
        }
        
        document.getElementById(pressedKey[K_ID]).classList.add("pressed");
        console.log(pressedKey[K_ID]);
        
    }
}

function keyReleased(e) {
    var releasedKey = keyMap[e.keyCode];
    if (releasedKey) {
        if (releasedKey[K_SIGNAL] === 'TOGGLE') {
            lightPressedTime = 0;
        }
        document.getElementById(releasedKey[K_ID]).classList.remove("pressed");
        console.log(releasedKey[K_ID] + " released");
        // socket.emit('released', releasedKey[K_SIGNAL] + "R")
    }
}

// function toggleLight(status) {
//     lightOn = status;
//     // console.log("LIGHT " + status);

//     lightToggler = document.getElementById("space");
//     if (lightOn) {
//         console.log("LIGHT ON");
//         lightToggler.classList.add("active");
//     } else {
//         console.log("LIGHT OFF");
//         lightToggler.classList.remove("active");
//     }

//     lightToggler.classList.remove("pressed");
// }

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
