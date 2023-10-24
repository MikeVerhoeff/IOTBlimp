#define STOP_CHAR 'e'

#include "Settings.h"

Settings settings;

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
  settings.addSensorInterface(&a0);
  settings.addSensorInterface(&a1);
  settings.addSensorInterface(&a2);
  
  // put your setup code here, to run once:
  Serial.begin(9600);
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
    else if(c=='f') {
      int newf = Serial.parseInt();
      settings.setFrequency(newf);
    }
    else if(c=='F') {
      settings.printFrequency();
    }
    else if(c=='i') {
      while(Serial.available()<0) {}
      char interface = Serial.read();
      settings.selectInterface(interface);
    }
    else if(c=='I') {
      settings.printSelectedInterface();
    }
    else if(c=='l') {
      settings.listSensorInterfaces();
    }
    else if(c=='c') {
      int num = Serial.parseInt();
      settings.run_times(num);
    }
    else if(c=='t') {
      int t = Serial.parseInt();
      settings.run_seccond(t);
    }
    else {
      while(Serial.available()<0)
      Serial.write(c);
    }
    
  }
}
