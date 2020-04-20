/*------------------------------------------------------------*-
  Library for controlling PS2X controller with Raspberry Pi
  Tested on: Raspberry Pi 3B/3B+
  (c) Minh-An Dao 2020  <bit.ly/DMA-HomePage>.
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

            
 --------------------------------------------------------------*/
#ifndef __PI_PS2X_CPP
#define __PI_PS2X_CPP
#include "pi_ps2x.h"


// ------ Private constants -----------------------------------
// --- Defaults, change with command-line options
#define SPI_CHANNEL 0
#define SPI_SPEED   500000 //500kHz
// #define CTRL_BYTE_DELAY  5   //us
// #define CTRL_CLK         5   //us
// #define UPDATE_INTERVAL  70  //ms
// #define EXPIRED_INTERVAL 1.5 //s

/* --- Modes
# Controller defaults to digital mode (0x41)
# It will only transmits the on / off status of the buttons in the 4th and 5th byte.
# No joystick data, pressure or vibration control capabilities.
*/
// static byte begin_request[]    = {0x01,0x42,0x00,0x00,0x00};
static byte begin_request[]    = {0x01,0x42,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
static byte enter_config[]     = {0x01,0x43,0x00,0x01,0x00};
// Once in config / escape mode, all packets will have 9 bytes (6 bytes of command / data after the header).
static byte type_read[]        = {0x01,0x45,0x00,0x5A,0x5A,0x5A,0x5A,0x5A,0x5A};
static byte set_mode_analog[]  = {0x01,0x44,0x00,0x01,0x03,0x00,0x00,0x00,0x00};
static byte set_mode_digital[] = {0x01,0x44,0x00,0x00,0x03,0x00,0x00,0x00,0x00};
static byte enable_pressure[]  = {0x01,0x4F,0x00,0xFF,0xFF,0x03,0x00,0x00,0x00};
static byte enable_rumble[]    = {0x01,0x4D,0x00,0x00,0x01,0xFF,0xFF,0xFF,0xFF};
static byte exit_config[]      = {0x01,0x43,0x00,0x00,0x5A,0x5A,0x5A,0x5A,0x5A};

// -----------data frame  {0x01,0x42,0x00,Motor1,Motor2,0x00,0x00,0x00,0x00}
byte data_frame[] = {0x01,0x42,0x00,0x00,0x00,0x00,0x00,0x00,0x00};

// --- DualShock button bit
#define SELECT     0x0001
#define L3         0x0002
#define R3         0x0004
#define START      0x0008
#define UP         0x0010
#define RIGHT      0x0020
#define DOWN       0x0040
#define LEFT       0x0080
#define L2         0x0100
#define R2         0x0200
#define L1         0x0400
#define R1         0x0800
#define TRIANGLE   0x1000
#define CIRCLE     0x2000
#define CROSS      0x4000
#define SQUARE     0x8000

// --- stick adc address
#define R_STICK_X 5
#define R_STICK_Y 6
#define L_STICK_X 7
#define L_STICK_Y 8

// --- simple logic functions
#define SET(x,y) (x|=(1<<y))
#define CLR(x,y) (x&=(~(1<<y)))
#define CHK(x,y) (x & (1<<y))
#define TOG(x,y) (x^=(1<<y))

// ------ Private function prototypes -------------------------

// ------ Private variables -----------------------------------

// ------ PUBLIC variable definitions -------------------------

//--------------------------------------------------------------
// FUNCTION DEFINITIONS
//--------------------------------------------------------------
PS2X::PS2X(int channel = SPI_CHANNEL, int speed = SPI_SPEED, bool analog_enable = true, bool pressure_enable = false, bool rumble_enable = false)
{
    /*
        Constructor
        @param analog_enable: a boolean indicates the analog mode of the PS2
        @param en_Pressures: a boolean indicates the pressure function of the PS2
        @param en_Rumble: a boolean indicates the rumble function of the PS2
    */
    this->spi_channel = channel;
    this->spi_speed = speed;
    this->en_analog = analog_enable;
    this->en_pressure = pressure_enable;
    this->en_rumble = rumble_enable;
    printf("speed: %d\n",this->spi_speed);
    printf("channel: %d\n",this->spi_channel);
    
   //---------------------- Setup wiringPi -----------------------
    wiringPiSetup();
    if ((this->myspi = wiringPiSPISetup (this->spi_channel, this->spi_speed)) < 0)
    {
        fprintf (stderr, "Can't open the SPI bus: %s\n", strerror (errno)) ;
        exit (EXIT_FAILURE) ;
    }
    
    unsigned int watchdog = millis();
    while (1) 
    {
        // begin sending request to the read gamepad
        // to see if it's responding or not
        this->__shiftout(begin_request);

        /*All mode:
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
        */
            
        //check if valid mode came back.
        if (this->message[1] == 0x41 || this->message[1] == 0x73 ||
            this->message[1] == 0x79 || this->message[1] == 0xF1 ||
            this->message[1] == 0xF3 || this->message[1] == 0xF9 )
        {break;}
        
        if ((millis() - watchdog) > 500) // one second to connect, if not connected then raise error
        {
            fprintf(stderr, "No controller found, please check wiring again.\n"); //# no controller found, expected 0x41, 0x42, 0x73 or 0x79
            exit(1);
        }//end if
    }//end while

    // ------ entering config mode
    this->__shiftout(enter_config);

    // --- get controller type
    byte controller_type = 0xFF;
    this->__shiftout(type_read);
    // if package header is correct [0xFF,0xF1-0xF3-0xF9,0x5A]
    if ((this->message[0] == 0xFF) && (this->message[2] == 0x5A))
        {controller_type = this->message[3];} // this is exactly what we want

    // --- config the controller as we want
    this->__shiftout(set_mode_analog);
    if (this->en_rumble)   {this->__shiftout(enable_rumble);}
    if (this->en_pressure) {this->__shiftout(enable_pressure);}
    this->__shiftout(exit_config);

    // ------- Done first config, now check response of the system
    watchdog = millis();
    while (1)
    {
        this->__shiftout(data_frame); // read to see if new data is comming

        if ((this->message[1] & 0xf0) == 0x70) {
            printf("Analog Mode");
            if (this->en_pressure) {
                if (this->message[1] == 0x79) {printf("Pressures mode");}
                if (this->message[1] == 0x73) {printf("Controller refusing to enter Pressures mode, may not support it.");}
                break;
            }
        } else if (this->message[1] == 0x41) {printf("Digital Mode"); break;}
        
        if ((millis() - watchdog) > 1000) // one second to connect, if not connected then raise error
        {
            fprintf(stderr, "Controller found but not in an recognizable mode: %02X\n",message[1]);
            exit(1);
        }//end if
    }//end while

    printf("Configured successful. Controller:");
    if      (controller_type == 0x03) {printf("DualShock");}
    else if (controller_type == 0x01) {printf("GuitarHero (Not supported yet)");}
    else if (controller_type == 0x0C) {printf("2.4G Wireless DualShock");}
    else if (controller_type == 0xFF) {printf("Wrong package header. Please check again");}
    else                              {printf("Unknown type");}

}//end constructor

PS2X::~PS2X()
{
    close(this->myspi);
}//end destructor

void PS2X::__shiftout(byte* command)
{   
    byte mes[sizeof(command)+1];
    unsigned int i;
    memcpy(mes, command, sizeof(mes));
    printf("Sent: "); for (i=0;i<sizeof(mes);i++) {printf("0x%02X,", *(mes+i));}
    printf("\n");
    if (wiringPiSPIDataRW (this->spi_channel, mes, sizeof(mes)) == -1)
	{
	  printf ("SPI failure: %s\n", strerror (errno)) ;
	  exit(1);
	}
    memcpy(this->message, mes, sizeof(mes));
    printf("Received: "); for (i=0;i<sizeof(this->message);i++) {printf("0x%02X,", *(this->message+i));}
    printf("\n");

    return;
}//end __shiftout

#endif //__PI_PS2X_CPP
