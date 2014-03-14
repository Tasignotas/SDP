// Arduino Code for SDP Group 7
// Rowan Border
// February 2014
// Attacker Code


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

// Servo
Servo grabber;

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
  
  comm.addCommand("A_SET_ENGINE", set_engine);
  comm.addCommand("A_RUN_ENGINE", run_engine);
  comm.addCommand("A_RUN_CATCH", run_catch); 
  comm.addCommand("A_RUN_KICK", run_kick); 
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


void run_kick()
{
  grabber.write(0);
  delay(450); // 0.15 sec/60 degrees * 3
  grabber.write(116);
}

void run_catch()
{
  grabber.write(132);
}


void invalid_command(const char *command)
{
}
