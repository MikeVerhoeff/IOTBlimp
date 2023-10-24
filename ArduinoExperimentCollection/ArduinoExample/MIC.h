#pragma once

namespace mic {
  
  void tick() {
    Serial.println(0);
  }


  SensorInterface mic_interface ('m', "MIC", tick);
  
  void addToUI(UI* ui) {
    ui->settings.addSensorInterface(&mic_interface);
  }
  
}
