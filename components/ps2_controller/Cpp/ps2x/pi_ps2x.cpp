/*------------------------------------------------------------*-
  Library for controlling PS2X controller with Raspberry Pi
  Tested on: Raspberry Pi 3B/3B+
  (c) Minh-An Dao 2020  <bit.ly/DMA-HomePage> <minhan7497@gmail.com>.
  version 1.00 - 19/04/2020
 --------------------------------------------------------------
 * Module created for the purpose of communicate 
 * with the PS2X controller.
 *
 * Ported from Arduino-PS2X library (https://github.com/madsci1016/Arduino-PS2X)
 * Documents:
 *  - https://store.curiousinventor.com/guides/PS2
 *  - https://gist.github.com/scanlime/5042071
 * 
 * Check out wiringPi pins, they are different from BCM pins (http://wiringpi.com/pins/)
 * ------ Pinout (wiringPi pins) ------
 * 13 - MISO  -  data (controller > pi)
 * 12 - MOSI  -  command (pi > controller)
 * 14 - SCLK  -  Clock
 * 10 - CE0   -  Attention (CS) (slave select)
 * 
 * All mode:
        0x41: Digital mode with ONE 16 bit words (2 bytes) follow the header.
                Contains only digital states of the buttons (byte 4 and byte 5)
        
        0x73: Analog mode with THREE 16 bit words (6 bytes) follow the header.
                Contain digital states of the buttons (byte 4 + byte 5)
                Contain 02 joystick ADC values:
                - Right Joystick (byte 6 + byte 7)
                - Left Joystick (byte 8 + byte 9)
        0x79: Analog mode with NINE 16 bit words (18 bytes) follow the header.
                Contain digital states of the buttons (byte 4 + byte 5)
                Contain 02 joystick ADC values:
                - Right Joystick (byte 6 + byte 7)
                - Left Joystick (byte 8 + byte 9)
                Contain adc value of 12 Button (pressures) (from byte 10 to byte 21) 
        
        0xFx: Config mode
 *
 * 
 * Usage: (root)
 * ./ps2x [-h] [-d DATA-pin] [-c CMD-pin] [-s SELECT-pin] [-k CLOCK-pin] [-a ANALOG] [-l LOCK] [-p PRESS] [-r RUMBLE] 
 *  With:
 *  -h            : show help
 *  -d DATA-pin   : GPIO pin for data pin (wiringPi pin)
 *  -c CMD-pin    : GPIO pin for command pin (wiringPi pin)
 *  -s SELECT-pin : GPIO pin for select pin (wiringPi pin)
 *  -k CLOCK-pin  : GPIO pin for data pin (wiringPi pin)
 *  -a ANALOG     : turn on or off analog mode (1 to turn on, 0 to turn off)
 *  -l LOCK       : turn on or off lock mode (1 to turn on, 0 to turn off)
 *  -p PRESS      : turn on or off pressure mode (1 to turn on, 0 to turn off)
 *  -r RUMBLE     : turn on or off rumble mode (1 to turn on, 0 to turn off)
 * 
 * Example: * Run as default:  sudo ./ps2x
 *          * Change pins:     sudo ./ps2x -d 9 -c 10 -s 8 -k 11
 *          * Change modes:    sudo ./ps2x -a 1 -l 1 -p 0 -r 1
 *
 * 
 * Licensed under the MIT license. All right reserved.
 --------------------------------------------------------------*/
#ifndef __PI_PS2X_CPP
#define __PI_PS2X_CPP
#include "pi_ps2x.h"


// ------ Private constants -----------------------------------
// --- Defaults, change with command-line options
#define CTRL_BYTE        20   //us - wait time between bytes transfer
#define CTRL_CLK         5   //us - clock source --> 200kHz
#define UPDATE_INTERVAL  50  //ms - wait time for other task to execute
#define EXPIRED_INTERVAL 1500 //ms
#define PS2_DAT 13  // wiringPi
#define PS2_CMD 12 // wiringPi
#define PS2_SEL 10  // wiringPi
#define PS2_CLK 14 // wiringPi
#define PS2_ANALOG true
#define PS2_LOCKED false
#define PS2_PRESSURE false
#define PS2_RUMBLE false
/* --- Modes
# Controller defaults to digital mode (0x41)
# It will only transmits the on / off status of the buttons in the 4th and 5th byte.
# No joystick data, pressure or vibration control capabilities.
*/
 byte begin_frame[]     = {0x01,0x42,0x00,0x00,0x00};
 byte enter_config[]    = {0x01,0x43,0x00,0x01,0x00};
// Once in config / escape mode, all packets will have 9 bytes (6 bytes of command / data after the header).
 byte type_read[]       = {0x01,0x45,0x00,0x5A,0x5A,0x5A,0x5A,0x5A,0x5A};
 byte enable_pressure[] = {0x01,0x4F,0x00,0xFF,0xFF,0x03,0x00,0x00,0x00};
 byte enable_rumble[]   = {0x01,0x4D,0x00,0x00,0x01,0xFF,0xFF,0xFF,0xFF};
 byte exit_config[]     = {0x01,0x43,0x00,0x00,0x5A,0x5A,0x5A,0x5A,0x5A};


// ------ Private function prototypes -------------------------
#define CHK(x,y) (x & (1<<y))
// ------ Private variables -----------------------------------
//default at analog, locked
//set_mode[3]=0x00 will change to digital mode
//set_mode[4]=0x00 will change to unlock mode (press the MODE button on the controller to change between analog and digital)
byte set_mode[]   = {0x01,0x44,0x00,0x01,0x03,0x00,0x00,0x00,0x00}; 
// --- data frame  {0x01,0x42,0x00,Motor1,Motor2,0x00,0x00,0x00,0x00}
byte data_frame[] = {0x01,0x42,0x00,0x00,0x00,0x00,0x00,0x00,0x00};

// ------ PUBLIC variable definitions -------------------------

//--------------------------------------------------------------
// FUNCTION DEFINITIONS
//--------------------------------------------------------------
PS2X::PS2X(int Dat = PS2_DAT,
           int Cmd = PS2_CMD,
           int Sel = PS2_SEL,
           int Clk = PS2_CLK,
           bool analog_enable = PS2_ANALOG,
           bool locked = PS2_LOCKED,
           bool pressure_enable = PS2_PRESSURE,
           bool rumble_enable = PS2_RUMBLE) {
    /*
        Constructor
        @param dat: an integer indicates the data pin of the PS2
        @param cmd: an integer indicates the command pin of the PS2
        @param sel: an integer indicates the select pin of the PS2
        @param clk: an integer indicates the clock pin of the PS2
        @param analog_enable: a boolean indicates the analog mode of the PS2
        @param pressure_enable: a boolean indicates the pressure function of the PS2
        @param rumble_enable: a boolean indicates the rumble function of the PS2
    */
    this->dat = Dat;
    this->cmd = Cmd;
    this->sel = Sel;
    this->clk = Clk;
    this->en_analog = analog_enable;
    this->en_locked = locked;
    this->en_pressure = pressure_enable;
    this->en_rumble = rumble_enable;
    this->last_buttons = 0;
    this->buttons = 0;
    this->last_Lsticks = 0;
    this->Lsticks = 0;

    this->changeMode(this->en_analog, this->en_locked);

   //---------------------- Setup wiringPi -----------------------
    wiringPiSetup();
    pinMode(this->dat, INPUT); pullUpDnControl(this->dat, PUD_UP);
    pinMode(this->cmd, OUTPUT);
    pinMode(this->sel, OUTPUT);
    pinMode(this->clk, OUTPUT);
    
    digitalWrite(this->cmd, HIGH); //CMD_SET
    digitalWrite(this->clk, HIGH); //CLK_SET
    digitalWrite(this->sel, HIGH); // SEL_SET - disable joystick
    
    unsigned int watchdog = millis();
    while (1) {
        // begin sending request to the read gamepad to see if it's responding or not
        this->__getData(begin_frame,5);

        //check if valid mode came back.
        if (this->ps2data[1] == 0x41 || this->ps2data[1] == 0x73 ||
            this->ps2data[1] == 0x79 || this->ps2data[1] == 0xF1 ||
            this->ps2data[1] == 0xF3 || this->ps2data[1] == 0xF9 )
        {break;}
        
        if ((millis() - watchdog) > 1000) // one second to connect, if not connected then raise error
        {
            fprintf(stderr, "No controller found, please check wiring again.\n"); //# no controller found, expected 0x41, 0x42, 0x73 or 0x79
            exit(EXIT_FAILURE);
        }//end if
    }//end while

    // ------ entering config mode
    this->__sendCommand(enter_config,5);

    // --- get controller type
    byte controller_type = 0xFF;
    this->__getData(type_read,9);
    // if package header is correct [0xFF,0xF1-0xF3-0xF9,0x5A]
    if ((this->ps2data[0] == 0xFF) && (this->ps2data[2] == 0x5A))
        {controller_type = this->ps2data[3];} // save type of the controller

    // --- config the controller as we want
    this->__sendCommand(set_mode,9);
    if (this->en_rumble)   {this->__sendCommand(enable_rumble,9);}
    if (this->en_pressure) {this->__sendCommand(enable_pressure,9);}
    this->__sendCommand(exit_config,9);

    // ------- Done first config, now check response of the system
    this->last_millis = millis(); // start system monitoring now
    watchdog = millis();
    printf("PS2 controller: ");
    while (1) {
        this->update(); // update to see if new data is comming

        if ((this->ps2data[1] & 0xf0) == 0x70) {
            printf("Analog Mode\n");
            if (this->en_pressure) {
                if (this->ps2data[1] == 0x79) {printf("Pressures mode is ON.\n");}
                if (this->ps2data[1] == 0x73) {fprintf(stderr, "Controller refusing to enter Pressures mode, may not support it.\n");}
            }//end if
            break;
        } else if (this->ps2data[1] == 0x41) {printf("Digital Mode\n"); break;}
        
        if ((millis() - watchdog) > 1000) // one second to connect, if not connected then raise error
        {
            fprintf(stderr, "Controller found but not in an recognizable mode: %02X\n",this->ps2data[1]);
            exit(EXIT_FAILURE);
        }//end if
    }//end while

    printf("Configure successful. Type: ");
    if      (controller_type == 0x03) {printf("DualShock\n");}
    else if (controller_type == 0x01) {printf("GuitarHero (Not supported yet)\n");}
    else if (controller_type == 0x0C) {printf("2.4G Wireless DualShock\n");}
    else if (controller_type == 0xFF) {printf("\nWrong package header. Please check again\n");}
    else                              {printf("Unknown type\n");}
}//end constructor

PS2X::~PS2X() {}//end destructor

//CAUTION: must call reconfig to update the changes
void PS2X::changeMode(bool analog_mode, bool locked_mode)
{
    set_mode[3] = (analog_mode)?0x01:0x00; //change between analog and digital mode
    set_mode[4] = (locked_mode)?0x03:0x00; //change between lock and unlock mode (press the MODE button on the controller to change between analog and digital)
}//end changeMode

//CAUTION: must call reconfig to update the changes
void PS2X::changeMode(bool analog_mode, bool locked_mode, bool pressure_mode, bool rumble_mode)
{
    this->changeMode(analog_mode,locked_mode);
    this->en_pressure = (pressure_mode)?true:false; //turn on-off pressure mode
    this->en_rumble = (rumble_mode)?true:false; //turn on-off rumble mode
}//end changeMode


void PS2X::reconfig(void) // must be called after changing mode, else it will makes no effects
{
    this->__sendCommand(enter_config,5);
    this->__sendCommand(set_mode,9);
    if (this->en_rumble)   {this->__sendCommand(enable_rumble,9);}
    if (this->en_pressure) {this->__sendCommand(enable_pressure,9);}
    this->__sendCommand(exit_config,9);
}//end reconfig

void PS2X::update(void)
{
    unsigned long now = millis() - this->last_millis;

    if (now>EXPIRED_INTERVAL) { //waited too long
        fprintf(stdout, "Waited too long. Try to reset...\n");
        this->last_millis = millis();
        this->reconfig();
        return;
    }//end if

    if (now<UPDATE_INTERVAL) {delay(UPDATE_INTERVAL-now);} //wait a little bit longer, give time for other tasks to complete

    this->__getData(data_frame,9);

    // Check to see if we received valid data or not.  
    // We should be in digital mode (0x41) or analog mode (0x73, 0x79)
    if ((this->ps2data[1] == 0x41)||
        (this->ps2data[1] == 0x73)||
        (this->ps2data[1] == 0x79)){
        // store the previous buttons states before get the new one
        this->last_buttons = this->buttons;
        // Byte 4 and 5 of the data is the status of all buttons
        // store as one variable
        this->buttons = (this->ps2data[4] << 8) + this->ps2data[3];
        // Store the previous stick states before get the new one
        this->last_Lsticks = this->Lsticks;
        // Byte ,8,9 are the status of the Left sticks
        // store as one variable.
        // You can add another one for Right one if you like. in my application scope I don't need it, so I didn't create it.
        this->Lsticks = (this->ps2data[7] << 8) + this->ps2data[8];

        this->last_millis = millis();
    } else if ((this->ps2data[1]&0xF0) == 0xF0) { //Check if we are in config mode (0xFx), if yes, reconfig to return to normal
        fprintf(stdout, "Currently in config mode. Getting out...\n");
        for (int x=0;x<21;x++) {this->ps2data[x] = 0;} //if not valid, then reset the whole frame 
        this->reconfig(); // try to get back to normal mode.
    } else {//not good data received
        fprintf(stdout, "Not valid header received: 0x%02X 0x%02X 0x%02X\n", this->ps2data[0],this->ps2data[1], this->ps2data[2]);
        for (int x=0;x<21;x++) {this->ps2data[x] = 0;} //if not valid, then reset the whole frame 
        delay(UPDATE_INTERVAL); //stablize time
    }// end if else
    return;
}//end update

bool PS2X::buttonChanged(void) {return (this->last_buttons^this->buttons)>0;}

bool PS2X::LstickChanged(void) {return (this->last_Lsticks^this->Lsticks)>0;} // You can add another one for Right one if you like. in my application scope I don't need it, so I didn't create it.

bool PS2X::changed(void) {return this->buttonChanged()|this->LstickChanged();}

bool PS2X::isPressing(int button) {return (~this->buttons&button)>0;}

bool PS2X::pressed(int button) {return this->buttonChanged()&this->isPressing(button);}

bool PS2X::released(int button) {return this->buttonChanged()&((~this->last_buttons&button)>0);}

int PS2X::rawButton(void) {return this->buttons;}

int PS2X::rawLastButton(void) {return this->last_buttons;}

int PS2X::rawLStick(void) {return this->Lsticks;}

int PS2X::rawLastLStick(void) {return this->last_Lsticks;}

/* WARNING: there are no analog value for SELECT, START, L3, R3.
            Please don't try put it in this function, otherwise result may not be what you're looking for
    5  - RX    9  - RIGHT    17 - L1                  16 - SQUARE - PINK
    6  - RY    12 - DOWN     18 - R1
    7  - LX    10 - LEFT     13 - TRIANGLE - GREEN
    8  - LY    19 - L2       14 - CIRCLE - RED
    11 - UP    20 - R2       15 - CROSS - BLUE
*/
int PS2X::readAnalog(int button) 
{
    int button_addr;
    button_addr = (button < 9)?button:0; //if button is analog stick
    if (!button_addr) // if button is other buttons
    {
        button_addr = (button == UP)?(11):((button == RIGHT)?(9):((button == DOWN)?(12):((button == LEFT)?(10):((button == L2)?(19):((button == R2)?(20):((button == L1)?(17):((button == R1)?(18):((button == TRIANGLE)?(13):((button == CIRCLE)?(14):((button == CROSS)?(15):((button == SQUARE)?(16):(0))))))))))));
    }//end if
    return this->ps2data[button_addr];    
}//end readAnalog

byte PS2X::__shiftout(byte command)
{   
    byte received = 0; // received data default to be 0
    for (int i=0;i<8;i++)
    {
        if (CHK(command, i)) {digitalWrite(this->cmd, HIGH);} // CMD_SET
        else                 {digitalWrite(this->cmd, LOW);}  // CMD_CLR
        
        digitalWrite(this->clk, LOW); // CLK_CLR
        delayMicroseconds(CTRL_CLK);

        if (digitalRead(this->dat)) {received|=1<<i;}
            
        digitalWrite(this->clk, HIGH); // CLK_SET
        delayMicroseconds(CTRL_CLK);
    }//end for
        
    digitalWrite(this->cmd, HIGH); // CMD_SET
    delayMicroseconds(CTRL_BYTE);
    return received;
}//end __shiftout

int PS2X::__sendCommand(byte* command, int size)
{
    digitalWrite(this->sel, LOW); // SEL_CLR - enable joystick
    delayMicroseconds(CTRL_BYTE);
    for (int y=0;y<size;y++) {this->__shiftout(*(command+y));}
    digitalWrite(this->sel, HIGH); // SEL_SET - disable joystick
    delayMicroseconds(CTRL_BYTE);
    return 0;
}//end __sendCommand

int PS2X::__getData(byte* command, int size)
{
    // get new data
    digitalWrite(this->cmd, HIGH); //CMD_SET
    digitalWrite(this->clk, HIGH); //CLK_SET
    digitalWrite(this->sel, LOW);  //SEL_CLR - enable joystick
    delayMicroseconds(CTRL_BYTE);

    int x=0;
    // Send the command to get button and joystick data
    for (x=0;x<size;x++)
    {this->ps2data[x] = this->__shiftout(*(command+x));}

    //if controller is in full analog return mode
    // get the rest of the data
    if (this->ps2data[1]==0x79) {
        for (x=0;x<12;x++)
        {this->ps2data[x+9] = this->__shiftout(0);}
    }//end if

    digitalWrite(this->sel, HIGH); // SEL_SET - disable joystick
    delayMicroseconds(CTRL_BYTE);
    return 0;
}//end __getData

#endif //__PI_PS2X_CPP
