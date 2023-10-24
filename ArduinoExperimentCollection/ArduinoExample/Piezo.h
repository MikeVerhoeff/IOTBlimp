#pragma once

namespace piezo {

  const int PIEZO_FLEX_PIN = A1;
  const int PIEZO_FLOPPY_PIN = A2;
  
  void tick_flex() {
    Serial.println(analogRead(PIEZO_FLEX_PIN));
  }

  void tick_floppy() {
    Serial.println(analogRead(PIEZO_FLOPPY_PIN));
  }

  SensorInterface piezo_flex_interface ('p', "Piezo-Flex", tick_flex);
  SensorInterface piezo_floppy_interface ('z', "Piezo-Floppy", tick_floppy);
  
  void addToUI(UI* ui) {
    pinMode(PIEZO_FLEX_PIN, INPUT);
    pinMode(PIEZO_FLOPPY_PIN, INPUT);
    ui->settings.addSensorInterface(&piezo_flex_interface);
    ui->settings.addSensorInterface(&piezo_floppy_interface);
  }
  
}
