#include <Servo.h>
Servo myservo;

int servoPin = 2;

int servo_couple = 70;
int servo_uncouple = 88;
bool servo_iscoupled = false;

void toggle_servo() {
  myservo.attach(servoPin);
  delay(100);
  if(servo_iscoupled) {
    myservo.write(servo_uncouple);
  } else {
    myservo.write(servo_iscoupled);
  }
  delay(100);
  myservo.detach();
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
