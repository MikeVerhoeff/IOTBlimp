#pragma once

#ifndef ARDUINO_SAMD_NANO_33_IOT
  #include <PDM.h>
#else
  class Fake_PDM {
    public:
    Fake_PDM() {}
    int available() { return 1;}
    void end() {}
    void read(void* a, int b) {}
    void onReceive(void (*a)(void)) {}
    bool begin(int, int) {}
  };
  Fake_PDM PDM;
#endif

#include "Settings.h"
#include "record.h"

// Microphone, range: ...
const int THRESHOLD_MICROPHONE = 15000;
const int SMP_FREQUENCY = 16000;

short* buffer;
int head;

volatile int samplesRead;
int last_noise;

//butterworth cutoff: 5z 
float b[] = {9.62491303e-07, 1.92498261e-06, 9.62491303e-07};
float a[] = {-1, 1.9972232,  -0.99722705};
int yhist[] = {0, 0, 0};
float reshist[] = {0.0f, 0.0f, 0.0f};
const int BW_THRESHOLD_MICROPHONE = 10000;
// #define BW_FILTER_ENEBLED

// Called when mic has new recordings
//!!!!!!!!!!!!!!!!!!!!! Do not use print statements !!!!!!!!!!!!!!!!!!!!!
void onPDMdata() { 
  int bytesAvailable = PDM.available();
  if (bytesAvailable > 2*MIC_TOTAL_SIZE) bytesAvailable = 2*MIC_TOTAL_SIZE;
  samplesRead = bytesAvailable / 2;

  if(samplesRead + head > MIC_TOTAL_SIZE) {
    int read_after_head = 2*(MIC_TOTAL_SIZE - head);
    PDM.read(buffer + head, read_after_head);
    PDM.read(buffer, bytesAvailable - read_after_head);
  } else {
    PDM.read(buffer + head, bytesAvailable);
  }
  head = (head + samplesRead)%MIC_TOTAL_SIZE;
}

void test_mic() {
  static bool popped = false;

  if (!samplesRead) return;

  int start = head - samplesRead;
  if(start < 0) start += MIC_TOTAL_SIZE;

  for (int i = 0; i < samplesRead; i++) {
    int idx = (start + i)%MIC_TOTAL_SIZE;

    #ifdef BW_FILTER_ENEBLED
    // run filter:
    yhist[0] = (float)buffer[idx]; // shift input buffer
    yhist[1] = yhist[0];
    yhist[2] = yhist[1];
    
    reshist[2] = reshist[1]; // shift memory buffer
    reshist[1] = reshist[0];

    // calculate for new sample
    reshist[0] = b[0]*yhist[0] + b[1]*yhist[1] + b[2]*yhist[2] + a[1]*reshist[1] + a[2]*reshist[2];   

    // update buffer
    buffer[idx] = (short)reshist[0];
    popped |= buffer[idx] > BW_THRESHOLD_MICROPHONE;

    #else
    popped = abs(buffer[idx] - last_noise) > THRESHOLD_MICROPHONE;
    last_noise = buffer[idx];
    #endif
  }
  samplesRead = 0;

  if (popped) digitalWrite(LED_BUILTIN, HIGH);
  else digitalWrite(LED_BUILTIN, LOW);
}


void init_mic(int f, unsigned long t) {
  head = 0;
  samplesRead = 0;
  last_noise = 0;

  yhist[0] = 0;
  yhist[1] = 0;
  yhist[2] = 0;
  reshist[0] = 0.0f;
  reshist[1] = 0.0f;
  reshist[2] = 0.0f;
  
  if (f > t) {
    buffer = (short*)  calloc((t/f) * MIC_TOTAL_SIZE   , sizeof(short));
  } else buffer = (short*)  calloc(MIC_TOTAL_SIZE   , sizeof(short));


  PDM.onReceive(onPDMdata);
  if (!PDM.begin(1, SMP_FREQUENCY)) Serial.println("Failed to start MICROPHONE!");
}

void del_mic() {
  PDM.end();

  print("MIC:", buffer, head, MIC_TOTAL_SIZE);

  free(buffer);

  digitalWrite(LED_BUILTIN, LOW);
}
