// Arduino Code for SDP Group 7
// Rowan Border
// February 2014
// Defender Code


#include <SerialCommand.h>
#include <AccelStepper.h>
#include <AFMotor.h>
#include <Servo.h>


// Communications
SerialCommand comm;

// Steppers
AF_Stepper left_motor(48, 1);
AF_Stepper right_motor(48, 2);
AccelStepper left_stepper(left_backward, left_forward);
AccelStepper right_stepper(right_backward, right_forward);

// Servo
Servo catcher;

// Solenoid
int kicker = 2;

// Stepper Control Functions

void left_forward() {  
  left_motor.onestep(FORWARD, SINGLE);
}
void left_backward() {  
  left_motor.onestep(BACKWARD, SINGLE);
}
void right_forward() {  
  right_motor.onestep(FORWARD, SINGLE);
}
void right_backward() {  
  right_motor.onestep(BACKWARD, SINGLE);
}

void setup()
{
  Serial.begin(115200);
  
  comm.addCommand("D_SET_ENGINE", set_engine);
  comm.addCommand("D_RUN_ENGINE", run_engine);
  comm.addCommand("D_RUN_KICKER", run_kicker); 
  comm.addCommand("D_RUN_CATCHER", run_catcher); 
  comm.setDefaultHandler(invalid_command);
  
  left_stepper.setMaxSpeed(1000.0);
  left_stepper.setAcceleration(1000.0);
   
  right_stepper.setMaxSpeed(1000.0);
  right_stepper.setAcceleration(1000.0);
  
  catcher.attach(9);
  pinMode(kicker, OUTPUT);
}


void loop()
{
  comm.readSerial();
  
  if (left_stepper.distanceToGo() == 0 && right_stepper.distanceToGo() == 0)
  {
    left_motor.release();
    right_motor.release();
  }
  else
  {
    left_stepper.run();
    right_stepper.run(); 
  }
}


void set_engine()
{
  char *max_speed_left;
  char *accel_left;
  char *max_speed_right;
  char *accel_right;
  
  max_speed_left = comm.next();
  accel_left = comm.next();
  max_speed_right = comm.next();
  accel_right = comm.next();
  
  if (max_speed_left != NULL && 50 <= atoi(max_speed_left) && atoi(max_speed_left) <= 1000)
  {
    left_stepper.setMaxSpeed(atof(max_speed_left)); 
  }
  
  if (accel_left != NULL && 50 <= atoi(max_speed_left) && atoi(max_speed_left) <= 1000)
  {
    left_stepper.setAcceleration(atof(accel_left)); 
  }
  
  if (max_speed_right != NULL && 50 <= atoi(max_speed_left) && atoi(max_speed_left) <= 1000)
  {
    right_stepper.setMaxSpeed(atof(max_speed_right)); 
  }
  
  if (accel_right != NULL && 50 <= atoi(max_speed_left) && atoi(max_speed_left) <= 1000)
  {
    right_stepper.setAcceleration(atof(accel_right)); 
  }
}


void run_engine()
{
  char *left_steps;
  char *right_steps;
  
  left_steps = comm.next();
  right_steps = comm.next();
  
  if (left_steps != NULL)
  {
    left_stepper.move(atoi(left_steps)); 
  }
  
  if (right_steps != NULL)
  {
    right_stepper.move(atoi(right_steps)); 
  }
}


void run_kicker()
{
  digitalWrite(kicker, HIGH);
  delay(80);
  digitalWrite(kicker, LOW);
}


void run_catcher()
{
  char *pos;
  
  pos = comm.next();
  if (pos != NULL)
  {
    catcher.write(atoi(pos)); 
  }
}


void invalid_command(const char *command)
{
}
