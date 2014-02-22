// Arduino Code for SDP Group 7
// Rowan Border
// February 2014


#include <SerialCommand.h>
#include <AccelStepper.h>
#include <AFMotor.h>
#include <Servo.h>


// Communications
SerialCommand comm;

// Steppers
AF_Stepper left_motor(48, 1);
AF_Stepper right_motor(48, 2);
AccelStepper left_stepper(left_forward, left_backward);
AccelStepper right_stepper(right_forward, right_backward);

// Servos
Servo kicker;
Servo catcher;


void setup()
{
  Serial.begin(9600);
  
  comm.addCommand("SET_ENGINE", set_engine);
  comm.addCommand("RUN_ENGINE", run_engine);
  comm.addCommand("RUN_KICKER", run_kicker); 
  comm.addCommand("RUN_CATCHER", run_catcher); 
  comm.setDefaultHandler(invalid_command);
  
  left_stepper.setMaxSpeed(1000.0);
  left_stepper.setAcceleration(100.0);
   
  right_stepper.setMaxSpeed(1000.0);
  right_stepper.setAcceleration(100.0);
    
  kicker.attach(9);
  catcher.attach(10);
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
  
  if (max_speed_left != NULL && 50 <= atof(max_speed_left) <= 1000)
  {
    left_stepper.setMaxSpeed(atof(max_speed_left)); 
  }
  else
  {
    Serial.println("Invalid Left Motor Speed Maximum");
  }
  
  if (accel_left != NULL && 50 <= atof(accel_left) <= 1000)
  {
    left_stepper.setAcceleration(atof(accel_left)); 
  }
  else
  {
    Serial.println("Invalid Left Motor Acceleration");
  }
  
  if (max_speed_right != NULL && 50 <= atof(max_speed_right) <= 1000)
  {
    right_stepper.setMaxSpeed(atof(max_speed_right)); 
  }
  else
  {
    Serial.println("Invalid Right Motor Speed Maximum");
  }
  
  if (accel_right != NULL && 50 <= atof(accel_right) <= 1000)
  {
    right_stepper.setAcceleration(atof(accel_right)); 
  }
  else
  {
    Serial.println("Invalid Right Motor Acceleration");
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
  char *pos;
  
  pos = comm.next();
  if (pos != NULL)
  {
    kicker.writeMicroseconds(atoi(pos)); 
  }
}


void run_catcher()
{
  char *pos;
  
  pos = comm.next();
  if (pos != NULL)
  {
    catcher.writeMicroseconds(atoi(pos)); 
  }
}


void invalid_command(const char *command)
{
  Serial.println("Invalid Command Received"); 
}


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
