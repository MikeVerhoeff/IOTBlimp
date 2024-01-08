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

int allocated_mic_size = 0;

short* buffer;
int head;

volatile int samplesRead;
volatile bool initFinished;
int last_noise;

//butterworth cutoff: 5z 
float b[] = {9.62491303e-07, 1.92498261e-06, 9.62491303e-07};
float a[] = {-1, 1.9972232,  -0.99722705};
int yhist[] = {0, 0, 0};
float reshist[] = {0.0f, 0.0f, 0.0f};
const int BW_THRESHOLD_MICROPHONE = 10000;
#define BW_FILTER_ENEBLED

// Called when mic has new recordings
//!!!!!!!!!!!!!!!!!!!!! Do not use print statements !!!!!!!!!!!!!!!!!!!!!
void onPDMdata() {
  int bytesAvailable = PDM.available();

  if(!initFinished) {
    short tmp[16];
    while(bytesAvailable>0) {
      if(bytesAvailable>16) {
        PDM.read(tmp, 16);
        bytesAvailable -= 16;
      } else {
        PDM.read(tmp, bytesAvailable);
        bytesAvailable = 0;
      }
    }
    return;
  }
  
  if (bytesAvailable > 2*allocated_mic_size) bytesAvailable = 2*allocated_mic_size;
  samplesRead = bytesAvailable / 2;
  
  if(samplesRead + head > allocated_mic_size) {
    int read_after_head = 2*(allocated_mic_size - head);
    PDM.read(buffer + head, read_after_head);
    PDM.read(buffer, bytesAvailable - read_after_head);
  } else {
    PDM.read(buffer + head, bytesAvailable);
  }
  head = (head + samplesRead)%allocated_mic_size;
}

short test_mic() {
  initFinished = true;
  //static bool popped = false;
  bool popped = false;

  if (!samplesRead) return 0;

  int start = head - samplesRead;
  if(start < 0) start += allocated_mic_size;

  short max_val = 0;
  
  for (int i = 0; i < samplesRead; i++) {
    int idx = (start + i)%allocated_mic_size;

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

    max_val = max(max_val, buffer[idx]);
    
    //buffer[idx] = buffer[idx] - BW_THRESHOLD_MICROPHONE;
    //if(popped) {
    //  buffer[idx] = -buffer[idx];
    //}
  }
  samplesRead = 0;

  //if (popped) digitalWrite(LED_BUILTIN, HIGH);
  //else digitalWrite(LED_BUILTIN, LOW);

  return max_val;
}


void init_mic(int f, unsigned long n) {
  
  if(n==0) {
    n = 256;
  }
  
  head = 0;
  samplesRead = 0;
  last_noise = 0;
  initFinished = false;

  yhist[0] = 0;
  yhist[1] = 0;
  yhist[2] = 0;
  reshist[0] = 0.0f;
  reshist[1] = 0.0f;
  reshist[2] = 0.0f;

  
  //MIC_TOTAL_SIZE = 16 * 1024 * ((t+f-1)/f) * 2;
  //buffer = (short*)  calloc(MIC_TOTAL_SIZE   , sizeof(short));
  
  //if (f > n) { // if recording longer than 1 seccond
    int t = (n+f-1)/f;
    allocated_mic_size = t * MIC_TOTAL_SIZE;
    buffer = (short*)  calloc(allocated_mic_size   , sizeof(short));
  //} else buffer = (short*)  calloc(MIC_TOTAL_SIZE   , sizeof(short));


  PDM.onReceive(onPDMdata);
  if (!PDM.begin(1, SMP_FREQUENCY)) Serial.println("Failed to start MICROPHONE!");
  delay(1000);
}

void del_mic() {
  PDM.end();

  print("MIC:", buffer, head, allocated_mic_size);
  allocated_mic_size = 0;
  free(buffer);

  digitalWrite(LED_BUILTIN, LOW);
}
