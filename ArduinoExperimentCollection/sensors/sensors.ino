#include "Settings.h"
#include "SensorInterface.h"
#include "proximity_sensor.h"
#include "microphone.h"
#include "piezo.h"
#include "gyroscope.h"
#include "accelerometer.h"

Settings settings;

Gyroscope     gyr;
Accelerometer acc;
Piezo         pie_flex(A1, 50);
Piezo         pie_hard(A2, 500);
Proximity     pro;

// Semi-individual sensors
SensorInterface imu_i ('b', "imu"     , [](int f, unsigned long t){   acc.init(f, t); gyr.init(f, t); }, [](){  acc.test(); gyr.test();     }, [](){  acc.del(); gyr.del(); });
SensorInterface pie_f ('e', "pie_flex", [](int f, unsigned long t){   pie_flex.init(f, t);            }, [](){  pie_flex.test();            }, [](){  pie_flex.del();       });
SensorInterface pie_h ('f', "pie_hard", [](int f, unsigned long t){   pie_hard.init(f, t);            }, [](){  pie_hard.test();            }, [](){  pie_hard.del();       });
SensorInterface mic_i ('a', "mic"     , [](int f, unsigned long t){   init_mic(f, t);                 }, [](){  test_mic();                 }, [](){  del_mic();            });
SensorInterface acc_i ('c', "acc"     , [](int f, unsigned long t){   acc.init(f, t);                 }, [](){  acc.test();                 }, [](){  acc.del();            });
SensorInterface gyr_i ('d', "gyr"     , [](int f, unsigned long t){   gyr.init(f, t);                 }, [](){  gyr.test();                 }, [](){  gyr.del();            });
SensorInterface pro_i ('g', "pro"     , [](int f, unsigned long t){   pro.init(f, t);                 }, [](){  pro.test();                 }, [](){  pro.del();            });

// Combinations
SensorInterface piezos ('h', "piezos" , 
                        [](int f, unsigned long t){   pie_flex.init(f, t); pie_hard.init(f, t); }, 
                        [](){                         pie_flex.test()    ; pie_hard.test()    ; }, 
                        [](){                         pie_flex.del()     ; pie_hard.del()     ; });
SensorInterface piezos_imu ('i', "pie_hard/imu" , 
                        [](int f, unsigned long t){   pie_hard.init(f, t); acc.init(f, t); }, 
                        [](){                         pie_hard.test()    ; acc.test()    ; }, 
                        [](){                         pie_hard.del()     ; acc.del()     ; });
SensorInterface all ('j', "all", 
                        [](int f, unsigned long t){   acc.init(f, t); pie_hard.init(f, t); pro.init(f, t); },
                        [](){                         acc.test()    ; pie_hard.test()    ; pro.test()    ; },
                        [](){                         acc.del()     ; pie_hard.del()     ; pro.del()     ; });

void setup() {
  settings.addSensorInterface(&mic_i);
  settings.addSensorInterface(&imu_i);
  settings.addSensorInterface(&acc_i);
  settings.addSensorInterface(&gyr_i);
  settings.addSensorInterface(&pie_f);
  settings.addSensorInterface(&pie_h);
  settings.addSensorInterface(&pro_i);
  settings.addSensorInterface(&piezos);
  settings.addSensorInterface(&piezos_imu);
  settings.addSensorInterface(&all);


  Serial.begin(115200);
  while(!Serial);

  pinMode(LED_BUILTIN, OUTPUT);
};

void loop() {
  if(Serial.available()>0) {
    char c = Serial.read();
    if(c=='f') {
      int newf = Serial.parseInt();
      settings.setFrequency(newf);
    }
    else if(c=='F') {
      settings.printFrequency();
    }
    else if(c=='i') {
      while(Serial.available()<0) {}
      char interface = Serial.read();
      settings.selectInterface(interface);
    }
    else if(c=='I') {
      settings.printSelectedInterface();
    }
    else if(c=='l') {
      settings.listSensorInterfaces();
    }
    else if(c=='c') {
      int num = Serial.parseInt();
      settings.run_times(num);
    }
    else if(c=='t') {
      int t = Serial.parseInt();
      settings.run_second(t);
    }
    else {
      while(Serial.available()<0)
      Serial.write(c);
    }
  }
}