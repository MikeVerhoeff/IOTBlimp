#pragma once

#include "Settings.h"
#include "Arduino_BMI270_BMM150.h"

  // Gyroscope, range: ...
const int THRESHOLD_XG = 200;
const int THRESHOLD_YG = 400;
const int THRESHOLD_ZG = 50;

class Gyroscope {
  private:
  int head;

  float* buff_x;
  float* buff_y;
  float* buff_z;

  public:
  Gyroscope() {}
  void init(int f, unsigned long t) {
    buff_x = (float*) calloc(t+1, sizeof(float));
    buff_y = (float*) calloc(t+1, sizeof(float));
    buff_z = (float*) calloc(t+1, sizeof(float));

    if (!IMU.begin()) Serial.println("Failed to initialize IMU!");

    while(!IMU.gyroscopeAvailable());
    IMU.readGyroscope(buff_x[0], buff_y[0], buff_z[0]);

    head = 1;
  }

  short test() {
    if (IMU.gyroscopeAvailable()) IMU.readGyroscope(buff_x[head], buff_y[head], buff_z[head]);
    else {
      buff_x[head] = buff_x[head-1];
      buff_y[head] = buff_y[head-1];
      buff_z[head] = buff_z[head-1];
    }

    head += 1;

    return 0;
  }

  void del() {
    print("GYR_X:", buff_x, head);
    print("GYR_Y:", buff_y, head);
    print("GYR_Z:", buff_z, head);

    free(buff_x);
    free(buff_y);
    free(buff_z);
    digitalWrite(LED_BUILTIN, LOW);
  }
};
