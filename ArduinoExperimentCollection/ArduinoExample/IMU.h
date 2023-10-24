#pragma once

#include <Arduino_LSM6DS3.h>

namespace imu {

  float ax, ay, az;
  float rx, ry, rz;
  
  void tick() {
    while(!IMU.accelerationAvailable()) {}
    while(!IMU.gyroscopeAvailable()) {}
    IMU.readAcceleration(ax, ay, az);
    IMU.readGyroscope(rx, ry, rz);
    Serial.print(ax);
    Serial.print(", ");
    Serial.print(ay);
    Serial.print(", ");
    Serial.print(az);
    Serial.print(", ");
    
    Serial.print(rx);
    Serial.print(", ");
    Serial.print(ry);
    Serial.print(", ");
    Serial.println(rz);
  }

  SensorInterface IMU_interface ('i', "IMU", tick);
  
  void addToUI(UI* ui) {
    if (!IMU.begin()) {
      Serial.println("Failed to initialize IMU!");
      while (1);
    }
    
    ui->settings.addSensorInterface(&IMU_interface);
  }
  
}
