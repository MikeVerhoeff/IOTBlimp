#pragma once

#include <Servo.h>
Servo myservo;

int servoPin = 2;

int servo_couple = 60;//70;
int servo_uncouple = 95;//88;
bool servo_iscoupled = false;

void toggle_servo() {
  myservo.attach(servoPin);
  delay(100);
  if(servo_iscoupled) {
    myservo.write(servo_uncouple);
  } else {
    myservo.write(servo_couple);
  }
  delay(100);
  myservo.detach();
}


void couple_servo() {
  if(!servo_iscoupled){
    myservo.attach(servoPin);
    myservo.write(servo_couple);
    delay(100);
    myservo.detach();
    servo_iscoupled = true;
  }
}

void uncouple_servo() {
  if(servo_iscoupled){
    myservo.attach(servoPin);
    myservo.write(servo_uncouple);
    delay(100);
    myservo.detach();
    servo_iscoupled = false;
  }
}

void transform_init(int f, unsigned long n) {
  delay(100);
  toggle_servo();
}

short tranfrom_test() {
  return 0;
}

void transfrom_delete() {
  
}
