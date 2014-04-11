// Arduino Code for SDP Group 7
// Rowan Border
// February 2014
// Attacker Code


#include <EEPROM.h>
#include <SerialCommand.h>
#include <AccelStepper.h>
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_PWMServoDriver.h"
#include <Servo.h>

// Speed Constants
int MAX_SPEED = 1000;
int MIN_SPEED = 50;
int MIN_STEP = 10;
int SHOOTING = 0;
int KICKING = 0;
int KICK_STEP;
int SHOOT_STEP;
int TURN_STEP;
int CATCH_POS;
int KICK_POS;
int GRAB_POS;

// Communications
SerialCommand comm;

// Motorshield
Adafruit_MotorShield AFMS = Adafruit_MotorShield();

// Steppers
Adafruit_StepperMotor *left_motor = AFMS.getStepper(48, 1);
Adafruit_StepperMotor *right_motor = AFMS.getStepper(48, 2);

// Stepper Control Functions
void left_forward() {  
  left_motor->onestep(FORWARD, DOUBLE);
}
void left_backward() {  
  left_motor->onestep(BACKWARD, DOUBLE);
}
void right_forward() {  
  right_motor->onestep(FORWARD, DOUBLE);
}
void right_backward() {  
  right_motor->onestep(BACKWARD, DOUBLE);
}

// AccelSteppers
AccelStepper left_stepper(left_backward, left_forward);
AccelStepper right_stepper(right_forward, right_backward);

// Servo
Servo grabber;


void setup()
{
  
  AFMS.begin();
  Serial.begin(115200);
  
  CATCH_POS = EEPROM.read(0);
  KICK_POS = EEPROM.read(1);
  GRAB_POS = EEPROM.read(2);
  SHOOT_STEP = EEPROM.read(3);
  KICK_STEP = EEPROM.read(4);
  TURN_STEP = EEPROM.read(5);
  
  comm.addCommand("A_SET_ENGINE", set_engine);
  comm.addCommand("A_SET_CATCH", set_catch);
  comm.addCommand("A_SET_KICK", set_kick);
  comm.addCommand("A_SET_FKICK", set_fkick);
  comm.addCommand("A_SET_GRAB", set_grab);
  comm.addCommand("A_SET_SHOOT", set_shoot);
  comm.addCommand("A_SET_TSHOOT", set_tshoot);
  comm.addCommand("A_RUN_ENGINE", run_engine);
  comm.addCommand("A_RUN_CATCH", run_catch); 
  comm.addCommand("A_RUN_KICK", run_kick);
  comm.addCommand("A_RUN_FKICK", run_fkick);
  comm.addCommand("A_RUN_GRAB", run_grab);
  comm.addCommand("A_RUN_SHOOT", run_shoot); 
  comm.setDefaultHandler(invalid_command);
  
  left_stepper.setMaxSpeed(MAX_SPEED);
  left_stepper.setAcceleration(MAX_SPEED);
   
  right_stepper.setMaxSpeed(MAX_SPEED);
  right_stepper.setAcceleration(MAX_SPEED);
  
  grabber.attach(10);
  run_grab();
}


void loop()
{
  if (SHOOTING == 1 || KICKING == 1)
  {
    Serial.flush();
  }
  else
  {
    comm.readSerial();
  }
  
  if (left_stepper.distanceToGo() == 0 && right_stepper.distanceToGo() == 0)
  {
    left_motor->release();
    right_motor->release();
    
    if (SHOOTING == 1 || KICKING == 1)
    {
      run_kick();
      SHOOTING = 0;
      KICKING = 0;
    }
  }
  else
  {
    left_stepper.run();
    right_stepper.run(); 
  }
}


void set_engine()
{
  char *left_in;
  char *right_in;
  int left_speed;
  int right_speed;
  
  left_in = comm.next();
  right_in = comm.next();
  
  if (left_in != NULL && right_in != NULL)
  {
      left_speed = atof(left_in);
      right_speed = atof(right_in);
      
      if (left_speed < MIN_SPEED)
      {
        left_speed = MIN_SPEED;
      }
      if (left_speed > MAX_SPEED)
      {
        left_speed = MAX_SPEED;
      }
      if (right_speed < MIN_SPEED)
      {
        right_speed = MIN_SPEED;
      }
      if (right_speed > MAX_SPEED)
      {
        right_speed = MAX_SPEED;
      }
      
      left_stepper.setMaxSpeed(left_speed);
      left_stepper.setAcceleration(left_speed);
      
      right_stepper.setMaxSpeed(right_speed);
      right_stepper.setAcceleration(right_speed);
      
  }
}


void set_catch()
{
    char *catch_in;
    
    catch_in = comm.next();
    
    if (catch_in != NULL)
    {
      CATCH_POS = atoi(catch_in);
      EEPROM.write(0, CATCH_POS);
    }
}


void set_kick()
{
    char *kick_in;
    
    kick_in = comm.next();
    
    if (kick_in != NULL)
    {
      KICK_POS = atoi(kick_in);
      EEPROM.write(1, KICK_POS);
    }
}


void set_grab()
{
    char *grab_in;
    
    grab_in = comm.next();
    
    if (grab_in != NULL)
    {
      GRAB_POS = atoi(grab_in);
      EEPROM.write(2, GRAB_POS);
    }
}


void set_shoot()
{
    char *shoot_in;
    
    shoot_in = comm.next();
    
    if (shoot_in != NULL)
    {
      SHOOT_STEP = atoi(shoot_in);
      EEPROM.write(3, SHOOT_STEP);
    }
}


void set_fkick()
{
    char *fkick_in;
    
    fkick_in = comm.next();
    
    if (fkick_in != NULL)
    {
      KICK_STEP = atoi(fkick_in);
      EEPROM.write(4, KICK_STEP);
    }
}


void set_tshoot()
{
    char *tshoot_in;
    
    tshoot_in = comm.next();
    
    if (tshoot_in != NULL)
    {
      TURN_STEP = atoi(tshoot_in);
      EEPROM.write(5, TURN_STEP);
    }
}


void run_engine()
{
  char *left_in;
  char *right_in;
  int left_step;
  int right_step;
  
  left_in = comm.next();
  right_in = comm.next();

  if (left_in != NULL && right_in != NULL)
  {
    left_step = atoi(left_in); 
    right_step = atoi(right_in);
    
    if (left_step < MIN_STEP && left_step > 0)
    {
      left_step = MIN_STEP; 
    }
    if (left_step > -MIN_STEP && left_step < 0)
    {
      left_step = -MIN_STEP; 
    }
    if (right_step < MIN_STEP && right_step > 0)
    {
      right_step = MIN_STEP; 
    }
    if (right_step > -MIN_STEP && right_step < 0)
    {
      right_step = -MIN_STEP; 
    }
    
    left_stepper.move(left_step);
    right_stepper.move(right_step);
    
  }
}


void run_catch()
{
  grabber.write(CATCH_POS);
}


void run_kick()
{
  grabber.write(KICK_POS);
  delay(500);
  run_grab();
}


void run_fkick()
{
  left_stepper.move(KICK_STEP);
  right_stepper.move(KICK_STEP);
  KICKING = 1;
  
  left_stepper.setMaxSpeed(MAX_SPEED);
  left_stepper.setAcceleration(MAX_SPEED);
      
  right_stepper.setMaxSpeed(MAX_SPEED);
  right_stepper.setAcceleration(MAX_SPEED);
}


void run_grab()
{
  run_catch();
  delay(175);
  grabber.write(GRAB_POS);
}


void run_shoot()
{
    char *turn_in;
    int turn_direction;
    
    turn_in = comm.next();
    
    if (turn_in != NULL)
    {
      turn_direction = atoi(turn_in);
      
      if (turn_direction == 1)
      {
        left_stepper.move(-SHOOT_STEP);
        right_stepper.move(SHOOT_STEP);
      }
      else
      {
        left_stepper.move(SHOOT_STEP);
        right_stepper.move(-SHOOT_STEP);
      } 
      SHOOTING = 1;
      
      left_stepper.setMaxSpeed(MAX_SPEED);
      left_stepper.setAcceleration(MAX_SPEED);
      
      right_stepper.setMaxSpeed(MAX_SPEED);
      right_stepper.setAcceleration(MAX_SPEED);
      
    }
}


void invalid_command(const char *command)
{
}
