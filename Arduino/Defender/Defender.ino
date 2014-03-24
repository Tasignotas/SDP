// Arduino Code for SDP Group 7
// Rowan Border
// February 2014
// Defender Code


#include <SerialCommand.h>
#include <AccelStepper.h>
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_PWMServoDriver.h"
#include <Servo.h>


// Communications
SerialCommand comm;

// Motorshield
Adafruit_MotorShield AFMStop(0x60);

// Steppers
Adafruit_StepperMotor *left_motor = AFMStop.getStepper(48, 1);
Adafruit_StepperMotor *right_motor = AFMStop.getStepper(48, 2);

// Stepper Control Functions
void left_forward() {  
  left_motor->onestep(FORWARD, SINGLE);
}
void left_backward() {  
  left_motor->onestep(BACKWARD, SINGLE);
}
void right_forward() {  
  right_motor->onestep(FORWARD, SINGLE);
}
void right_backward() {  
  right_motor->onestep(BACKWARD, SINGLE);
}

// AccelSteppers
AccelStepper left_stepper(left_forward, left_backward);
AccelStepper right_stepper(right_forward, right_backward);

// Servo
Servo grabber;


void setup()
{
  AFMStop.begin();
  Serial.begin(115200);
  
  comm.addCommand("D_SET_ENGINE", set_engine);
  comm.addCommand("D_RUN_ENGINE", run_engine);
  comm.addCommand("D_RUN_CATCH", run_catch); 
  comm.addCommand("D_RUN_KICK", run_kick); 
  comm.setDefaultHandler(invalid_command);
  
  left_stepper.setMaxSpeed(1000.0);
  left_stepper.setAcceleration(1000.0);
   
  right_stepper.setMaxSpeed(1000.0);
  right_stepper.setAcceleration(1000.0);
  
  grabber.attach(10);
  run_kick();
}


void loop()
{
  comm.readSerial();
  
  if (left_stepper.distanceToGo() == 0 && right_stepper.distanceToGo() == 0)
  {
    left_motor->release();
    right_motor->release();
  }
  else
  {
    left_stepper.run();
    right_stepper.run(); 
  }
}


void set_engine()
{
  char *left_speed;
  char *right_speed;
  
  left_speed = comm.next();
  right_speed = comm.next();
  
  if (left_speed != NULL && 50 <= atoi(left_speed) && atoi(left_speed) <= 1000)
  {
    left_stepper.setMaxSpeed(atof(left_speed));
    right_stepper.setAcceleration(atof(left_speed));
  }
  
  if (right_speed != NULL && 50 <= atoi(left_speed) && atoi(left_speed) <= 1000)
  {
    right_stepper.setMaxSpeed(atof(right_speed)); 
    right_stepper.setAcceleration(atof(right_speed)); 
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


void run_catch()
{
  grabber.write(180);
}


void run_kick()
{
  grabber.write(0);
  delay(500);
  grabber.write(165);
}


void invalid_command(const char *command)
{
}
