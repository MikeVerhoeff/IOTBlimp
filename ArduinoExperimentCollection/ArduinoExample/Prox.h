#pragma once

namespace prox {
  
  void tick() {
    Serial.println(0);
  }


  SensorInterface prox_interface ('m', "Proximity", tick);
  
  void addToUI(UI* ui) {
    ui->settings.addSensorInterface(&prox_interface);
  }
  
}
