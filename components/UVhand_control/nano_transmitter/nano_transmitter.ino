// ref: https://www.robot-electronics.co.uk/htm/srf05tech.htm

#include "ultrasonic.h"
#include "KalmanFilter.h"

#define TRIG_PIN 6
#define ECHO_PIN_01 7
#define ECHO_PIN_02 8
#define ECHO_PIN_03 9
#define ECHO_PIN_04 10
#define ECHO_PIN_05 11
#define ECHO_PIN_06 12

#define ALLOWED_ERROR 10

#define PROCESS_VARIANCE 0.1

Ultrasonic sensor01(TRIG_PIN, ECHO_PIN_01);  // Initialize sensor.
Ultrasonic sensor02(TRIG_PIN, ECHO_PIN_02);  // Initialize sensor.
Ultrasonic sensor03(TRIG_PIN, ECHO_PIN_03);  // Initialize sensor.
Ultrasonic sensor04(TRIG_PIN, ECHO_PIN_04);  // Initialize sensor.
Ultrasonic sensor05(TRIG_PIN, ECHO_PIN_05);  // Initialize sensor.
Ultrasonic sensor06(TRIG_PIN, ECHO_PIN_06);  // Initialize sensor.

/* KalmanFilter(e_mea, e_est, q);
e_mea: Measurement Uncertainty - How much do we expect to our measurement vary
e_est: Estimation Uncertainty - Can be initilized with the same value as e_mea since the kalman filter will adjust its value.
q: Process Variance - usually a small number between 0.001 and 1 - how fast your measurement moves. Recommended 0.01. Should be tunned to your needs.
*/
KalmanFilter filter01(10, 10, PROCESS_VARIANCE);
KalmanFilter filter02(10, 10, PROCESS_VARIANCE);
KalmanFilter filter03(10, 10, PROCESS_VARIANCE);
KalmanFilter filter04(10, 10, PROCESS_VARIANCE);
KalmanFilter filter05(10, 10, PROCESS_VARIANCE);
KalmanFilter filter06(10, 10, PROCESS_VARIANCE);

void setup () {
    Serial.begin(9600);  // Initialize serial communication
}

void loop () {
  int value01 = filter01.updateEstimate(sensor01.measure());
  int value02 = filter02.updateEstimate(sensor02.measure());
  int value03 = filter03.updateEstimate(sensor03.measure());
  int value04 = filter04.updateEstimate(sensor04.measure());
  int value05 = filter05.updateEstimate(sensor05.measure());
  int value06 = filter06.updateEstimate(sensor06.measure());
  //int value01 = sensor01.measure();
  //int value02 = sensor02.measure();
  //int value03 = sensor03.measure();
  //int value04 = sensor04.measure();
  //int value05 = sensor05.measure();
  //int value06 = sensor06.measure();
  Serial.print(value01); Serial.print(" "); 
  Serial.print(value02); Serial.print(" "); 
  Serial.print(value03); Serial.print(" "); 
  Serial.print(value04); Serial.print(" "); 
  Serial.print(value05); Serial.print(" "); 
  Serial.print(value06); Serial.print(" "); 
  Serial.print("\n");
}
