#pragma once

#include <Arduino_APDS9960.h>

namespace prox {
  
  void tick() {
    while(!APDS.proximityAvailable()) {}
    Serial.println(APDS.readProximity());
  }


  SensorInterface prox_interface ('m', "Proximity", tick);
  
  void addToUI(UI* ui) {
    if (!APDS.begin()) {
      Serial.println("Error initializing APDS9960 sensor!");
    }
    ui->settings.addSensorInterface(&prox_interface);
  }
  
}
