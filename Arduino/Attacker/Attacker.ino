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
  Serial.begin(9600);
  
  comm.addCommand("D_SET_ENGINE", set_engine);
  comm.addCommand("D_RUN_ENGINE", run_engine);
  comm.addCommand("D_RUN_KICKER", run_kicker); 
  comm.addCommand("D_OPEN_CATCHER", open_catcher); 
  comm.addCommand("D_CLOSE_CATCHER", close_catcher); 
  comm.setDefaultHandler(invalid_command);
  
  left_stepper.setMaxSpeed(1000.0);
  left_stepper.setAcceleration(1000.0);
   
  right_stepper.setMaxSpeed(1000.0);
  right_stepper.setAcceleration(1000.0);
  
  catcher.attach(10);
  pinMode(kicker, OUTPUT);
  open_catcher();
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
    left_stepper.setAcceleration(atof(left_speed)); 
  }
  
  if (right_speed != NULL && 50 <= atoi(right_speed) && atoi(right_speed) <= 1000)
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


void run_kicker()
{
  open_catcher();
  digitalWrite(kicker, HIGH);
  delay(500);
  digitalWrite(kicker, LOW);
}


void open_catcher()
{
  catcher.write(35);
  delay(300);
  catcher.write(40);
}


void close_catcher()
{
  catcher.write(85);
  delay(300);
  catcher.write(80);
}


void invalid_command(const char *command)
{
}
