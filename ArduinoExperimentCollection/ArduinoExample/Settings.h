#pragma once

#include "SensorInterface.h"

#define NUM_INTERFACES 10

class Settings {
private:
  SensorInterface* interfaces[NUM_INTERFACES] = {nullptr};
  unsigned long frequency = 250;
  int selected_interface = 0;
  
public:
  Settings() {
    
  }

  void addSensorInterface(SensorInterface* interface) {
    for(int i=0; i<NUM_INTERFACES; i++) {
      if(interfaces[i] == nullptr) {
        interfaces[i] = interface;
        return;
      }
    }
  }

  void listSensorInterfaces() {
    for(int i=0; i<NUM_INTERFACES && interfaces[i]!=nullptr; i++) {
      Serial.print(interfaces[i]->key);
      Serial.print(':');
      Serial.println(interfaces[i]->name);
    }
    Serial.println(STOP_CHAR);
  }

  void printFrequency() {
    Serial.print("frequency:");
    Serial.println(frequency);
  }

  void setFrequency(unsigned long f) {
    frequency = f;
  }

  unsigned long getFrequency() {
    return frequency;
  }

  void printSelectedInterface() {
    Serial.print("interface:");
    if(interfaces[selected_interface]!=nullptr) {
      Serial.println(interfaces[selected_interface]->name);
    } else {
      Serial.println("NONE");
    }
  }

  bool selectInterface(char interface) {
    for(int i=0; i<NUM_INTERFACES && interfaces[i]!=nullptr; i++) {
      if(interfaces[i]->key == interface) {
        selected_interface = i;
        return true;
      }
    }
    return false;
  }

  void run_seccond(int t) {
    run_times(t*frequency);
  }
  
  void run_times(unsigned long n) {
    unsigned long delta = 1000000/frequency;
    unsigned long next_time = micros();
    for(unsigned long i=0; i<n; i++) {
      unsigned long current_time;
      do {
        current_time = micros();
      } while(current_time < next_time);
      interfaces[selected_interface]->function();
      next_time += delta;
    }
    Serial.println(STOP_CHAR);
  }
  
};
