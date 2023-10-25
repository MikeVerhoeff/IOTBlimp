#define STOP_CHAR 'e'

#include "UI.h"
#include "Piezo.h"
#include "IMU.h"
#include "Prox.h"
#include "MIC.h"

UI ui;

void test0() {
  Serial.println(analogRead(A0));
}
void test1() {
  Serial.println(analogRead(A1));
}

void test2() {
  Serial.println("0");
}

SensorInterface a0 ('0', "A0", test0);
SensorInterface a1 ('1', "A1", test1);
SensorInterface a2 ('c', "Constant 0", test2);

void setup() {
  ui.settings.addSensorInterface(&a0);
  ui.settings.addSensorInterface(&a1);
  ui.settings.addSensorInterface(&a2);
  
  piezo::addToUI(&ui);
  imu::addToUI(&ui);
  prox::addToUI(&ui);
  mic::addToUI(&ui);
  
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(A0, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available()>0) {
    char c = Serial.read();
    if(c=='s') {
      for(int i=0; i<2048; i++) {
        Serial.println(analogRead(A0));
      }
      Serial.println(STOP_CHAR);
    }
    else if (!ui.handleInput(c)) {
      Serial.write(c);
    }
    
  }
}
