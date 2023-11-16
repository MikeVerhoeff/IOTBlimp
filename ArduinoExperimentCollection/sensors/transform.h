#pragma once

#include <Servo.h>
Servo myservo;

int servoPin = 2;

int servo_couple = 65; // 70
int servo_uncouple = 93; // 88
bool servo_iscoupled = true;

short couple_clutch() {
  if(!servo_iscoupled) {
    myservo.write(servo_couple);
    myservo.attach(servoPin);
    myservo.write(servo_couple);
    delay(200);
    myservo.detach();
    servo_iscoupled = true;
  }
  return 0;
}

short couple_unclutch() {
  if(servo_iscoupled) {
    myservo.write(servo_uncouple);
    myservo.attach(servoPin);
    myservo.write(servo_uncouple);
    delay(200);
    myservo.detach();
    servo_iscoupled = false;
  }
  return 0;
}

void toggle_servo() {
  //myservo.attach(servoPin);
  delay(100);
  
  servo_iscoupled = !servo_iscoupled;
}


void transform_void_init(int f, unsigned long n) {}
void transform_void_delete() {}

void transform_init(int f, unsigned long n) {
  delay(100);
  toggle_servo();
}

short tranfrom_test() {
  if(servo_iscoupled) {
    servo_iscoupled = false;
    //myservo.write(servo_uncouple);
    couple_clutch();
  } else {
    //myservo.write(servo_couple);
    servo_iscoupled = true;
    couple_unclutch();
  }
  delay(1);
  return 0;
}

void transfrom_delete() {
  delay(100);
  //myservo.detach();
}
