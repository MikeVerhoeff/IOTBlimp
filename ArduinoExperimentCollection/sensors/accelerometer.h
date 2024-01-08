#pragma once

#include "Settings.h"
#include "Arduino_BMI270_BMM150.h"

// Accelerometer, range: ...
const int THRESHOLD_XA = -1;
const int THRESHOLD_YA = 2;
const int THRESHOLD_ZA = 0;

class Accelerometer {
  private:
  int head;
  int offset;

  float* buff_x;
  float* buff_y;
  float* buff_z;

  public:
  Accelerometer() {}

  void init(int f, unsigned long t) {
    offset = 1;
    if(t==0) {
      t=1;
      offset = 0;
    }
    
    buff_x = (float*) calloc(t+1, sizeof(float));
    buff_y = (float*) calloc(t+1, sizeof(float));
    buff_z = (float*) calloc(t+1, sizeof(float));

    if (!IMU.begin()) Serial.println("Failed to initialize IMU!");

    while(!IMU.accelerationAvailable());
    IMU.readAcceleration(buff_x[0], buff_y[0], buff_z[0]);

    head = 1;
  }

  short test() {
    if (IMU.accelerationAvailable()) IMU.readAcceleration(buff_x[head], buff_y[head], buff_z[head]);
    else {
      buff_x[head] = buff_x[head-1];
      buff_y[head] = buff_y[head-1];
      buff_z[head] = buff_z[head-1];
    }
    
    float len = buff_x[head]*buff_x[head] + buff_y[head]*buff_y[head] + buff_z[head]*buff_z[head];
    /*if (len < 0.5f*0.5f) {
      digitalWrite(LED_BUILTIN, HIGH);
    } else {
      digitalWrite(LED_BUILTIN, LOW);
    }*/

    head += offset;
    return len*1000;
  }

  void del() {
    print("ACC_X:", buff_x, head);
    print("ACC_Y:", buff_y, head);
    print("ACC_Z:", buff_z, head);

    free(buff_x);
    free(buff_y);
    free(buff_z);
    digitalWrite(LED_BUILTIN, LOW);
  }

};
