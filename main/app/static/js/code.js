// ref: https://www.w3schools.com/jsref/dom_obj_event.asp
// document.addEventListener("keypress", keyPressed, false);
document.addEventListener("keydown", keyIsPressing, false);
document.addEventListener("keyup", keyReleased, false);

const K_SIGNAL = 0, K_ID = 1;

const keyMap = {
    87: ['UP', 'w', false],                          // W - UP
    65: ['LE', 'a', false],                          // A - LEFT
    68: ['RI', 'd', false],                          // D - RIGHT
    83: ['DO', 's', false],                          // S - DOWN
    72: ['LU', 'h', false],                          // H - LEFT HAND UP
    74: ['LD', 'j', false],                          // J - LEFT HAND DOWN
    75: ['RU', 'k', false],                          // K - RIGHT HAND UP
    76: ['RD', 'l', false],                          // L - RIGHT HAND DOWN
    81: ['SP', 'q',, false],                         // Q - SPEED CHANGE
    32: ['TG', 'space',, false],                     // Space - LIGHT CHANGE
};

var socket = io();
lastTime = new Date().getTime();
lightOn = 'OF'; //OFF
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
    } else { //OFF
        console.log("light off");
        lightToggler.classList.remove("active");
    }

    lightToggler.classList.remove("pressed");
});

socket.on('speed', (status) => {
    speedState = status;

    speedToggler = document.getElementById("q");
    if (speedState === 'HI') { //HIGH
        console.log("high speed mode");
        speedToggler.classList.add("active");
    } else { //LOW
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

        if (curTime - lastTime < 40) // ms
            return;

        lastTime = curTime;

        // ----------------------- toggle light function ------------------------
        if (pressedKey[K_SIGNAL] === 'TG') { //TOGGLE
            if ((lightOn === 'ON' && lightPressedTime === 0) ||
                (curTime - lightPressedTime > 1000 && lightOn === 'OF' && curTime - lightPressedTime < 1500)) {
                socket.emit('light');
                lightPressedTime = 1600;
            } else if (lightPressedTime === 0 && lightOn === 'OF') { //OFF
                lightPressedTime = new Date().getTime();
                document.getElementById(pressedKey[K_ID]).classList.add("pressed");
            }
            return;
        }
        // ----------------------- toggle speed function ------------------------
        if (pressedKey[K_SIGNAL] === 'SP') { //SPEED
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
        if (releasedKey[K_SIGNAL] === 'TG') { //TOGGLE
            lightPressedTime = 0;
        }
        document.getElementById(releasedKey[K_ID]).classList.remove("pressed");
        console.log(releasedKey[K_ID] + " released");
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
