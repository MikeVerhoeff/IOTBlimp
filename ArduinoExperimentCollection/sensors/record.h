#pragma once

#include "Settings.h"

void print(const char* name, float* buff, int head) {
  Serial.println(name);
  for(int i = 0; i < head; i++) {
    Serial.println(buff[i]);
  }
}

void print(const char* name, int* buff, int head) {
  Serial.println(name);
  for(int i = 0; i < head; i++) {
    Serial.println(buff[i]);
  }
}

void print(const char* name, short* buff, int head, int size) {
  Serial.println(name);
  for(int i = 0; i < size; i++) {
    Serial.println(buff[(i+head) % size]);
  }
}