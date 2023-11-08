#pragma once

#include "Settings.h"
#include "record.h"

#include <Arduino_APDS9960.h>

// Proximity sensor, range: 0-255
const int THRESHOLD_PROXIMITY = 150;

class Proximity {

  private:
  int* buffer;
  int head = 0;
  int last_value;

  public:

  void init(int f, unsigned long t) {
    buffer = (int*) calloc(t+1, sizeof(int));

    head = 0;
    if (!APDS.begin()) Serial.println("Error initializing PROXIMITY sensor!");
    while(!APDS.proximityAvailable());
    last_value = APDS.readProximity();
  }

  short test() {
    if(APDS.proximityAvailable()) buffer[head] = APDS.readProximity();
    else buffer[head] = last_value;

    //if(buffer[head] > THRESHOLD_PROXIMITY) 
    //  digitalWrite(LED_BUILTIN, HIGH);
    //else digitalWrite(LED_BUILTIN, LOW);

    last_value = buffer[head];
    head += 1;

    return last_value;
  }

  void del() {
    APDS.end();

    print("PROXIMITY:", buffer, head);

    free(buffer);
    digitalWrite(LED_BUILTIN, LOW);
  }
};
