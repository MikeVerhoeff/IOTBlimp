#pragma once

#include "Settings.h"

class UI {
private:
public:
  Settings settings;

  UI() {
    
  }

  bool handleInput(char c) {
    if(c=='f') {
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
      return false;
    }
    return true;
  }
};
