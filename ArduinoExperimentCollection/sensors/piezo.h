#pragma once

#include "settings.h"
#include "record.h"
#include <stdbool.h>

class Piezo {
  private:
  const int PIN;
  const int THRESHOLD;

  int head;
  int last_value;

  float* buffer;

  public:
  Piezo(const int pin, const int threshold) : PIN(pin), THRESHOLD(threshold) {}

  void init(int f, unsigned long t) {
    buffer = (float*) calloc(t+1, sizeof(float));

    pinMode(PIN, INPUT);

    head = 0;
    last_value = analogRead(PIN);
  }

  short test() {
    buffer[head] = analogRead(PIN);

    //if(abs(last_value - buffer[head]) > THRESHOLD) 
    //  digitalWrite(LED_BUILTIN, HIGH);
    //else digitalWrite(LED_BUILTIN, LOW);

    last_value = buffer[head];
    head += 1;

    return last_value;
  }

  
  void del() {
    print("PIEZO:", buffer, head);

    free(buffer);

    digitalWrite(LED_BUILTIN, LOW);
  }
};
