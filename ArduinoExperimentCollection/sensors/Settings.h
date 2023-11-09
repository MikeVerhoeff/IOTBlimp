#pragma once

#include "SensorInterface.h"

#define NUM_INTERFACES 10
#define STOP_CHAR 'e'

int MIC_BUFFER_SIZE = 1024;
uint32_t MIC_TOTAL_SIZE = 16*MIC_BUFFER_SIZE;


class Settings {
private:
  SensorInterface* interfaces[NUM_INTERFACES] = {nullptr};
  unsigned long frequency = 175;
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

  void run_second(int t) {
    run_times(t*frequency);
  }
  
  void run_times(unsigned long n) {
    digitalWrite(LED_BUILTIN, HIGH);
    interfaces[selected_interface]->init(frequency, n);
    for(int j=0; j<interfaces[selected_interface]->funcCount; j++) {
      interfaces[selected_interface]->functions[j].reset();
    }
    
    digitalWrite(LED_BUILTIN, LOW);
    delay(200);
    digitalWrite(LED_BUILTIN, HIGH);

    Serial.println("P_X:");
    unsigned long delta = 1000000/frequency;
    unsigned long next_time = micros();
    
    unsigned long current_time;
    for(unsigned long i=0; i<n || n==0; i++) {
      do {
        current_time = micros();
      } while(current_time < next_time);
      short p=0;
      for(int j=0; j<interfaces[selected_interface]->funcCount; j++) {
        p+=interfaces[selected_interface]->functions[j].run(current_time);
      }
      Serial.println(p);
      if(p>=interfaces[selected_interface]->threshold) {
        digitalWrite(LED_BUILTIN, HIGH);
      } else {
        digitalWrite(LED_BUILTIN, LOW);
      }
      next_time += delta;
      if(n==0 && Serial.available()>0) {
        char c = Serial.read();
        if(c=='e') {
          break;
        }
      }
    }
    digitalWrite(LED_BUILTIN, HIGH);
    interfaces[selected_interface]->del();
    Serial.println(STOP_CHAR);
    delay(100);
    Serial.println("stopped");
    Serial.print("Delta: ");
    Serial.println(delta);
    Serial.print("Overrun: ");
    Serial.print(current_time - (next_time-delta));
    Serial.println(" us");
    if(current_time - (next_time-delta) < delta) {
      Serial.println("Timing: OK");
    } else {
      Serial.println("Timing: Frequency to high");
    }
  }
  
};
