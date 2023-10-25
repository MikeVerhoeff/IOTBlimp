#pragma once

#ifndef ARDUINO_SAMD_NANO_33_IOT

#include <PDM.h>

namespace mic {

  // buffer to read samples into, each sample is 16-bits
  short sampleBuffer[256];
  
  // number of samples read
  volatile int samplesRead;

  void onPDMdata() {
    // query the number of bytes available
    int bytesAvailable = PDM.available();
  
    // read into the sample buffer
    PDM.read(sampleBuffer, bytesAvailable);
  
    // 16-bit, 2 bytes per sample
    samplesRead = bytesAvailable / 2;
  }


  
  void tick() {
    if (samplesRead) {
      // print samples to the serial monitor or plotter
      for (int i = 0; i < samplesRead; i++) {
        Serial.println(sampleBuffer[i]);
      }
      samplesRead = 0;
    }
  }


  SensorInterface mic_interface ('m', "MIC", tick);
  
  void addToUI(UI* ui) {
    // configure the data receive callback
    PDM.onReceive(onPDMdata);
  
    // optionally set the gain, defaults to 20
    // PDM.setGain(30);
  
    // initialize PDM with:
    // - one channel (mono mode)
    // - a 16 kHz sample rate
    if (!PDM.begin(1, 16000)) {
      Serial.println("Failed to start PDM!");
      while (1);
    }
    ui->settings.addSensorInterface(&mic_interface);
  }
  
}

#else
namespace mic {
  void addToUI(UI* ui) {
    
  }
}
#endif
