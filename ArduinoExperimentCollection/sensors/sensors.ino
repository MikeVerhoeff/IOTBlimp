#include "Settings.h"
#include "SensorInterface.h"
#include "proximity_sensor.h"
#include "microphone.h"
#include "piezo.h"
#include "gyroscope.h"
#include "accelerometer.h"
#include "transform.h"

Settings settings;

Gyroscope     gyr;
Accelerometer acc;
Piezo         pie_flex(A2, 50);
Piezo         pie_hard(A3, 500);
Proximity     pro;

short acc_off = 500;
short acc_on =  200;

short piezo_off = 300;
short piezo_on =  700;

short prox_off = 100;
short prox_on = 200;

short mic_off = 8000;
short mic_on = 10000;


// Semi-individual sensors
SensorInterface imu_i ('b', "imu"     , [](int f, unsigned long t){   acc.init(f, t); gyr.init(f, t); }, TestInfo([](){ gyr.test(); return acc.test();     }, acc_off,   acc_on  ),    [](){  acc.del(); gyr.del(); });
SensorInterface pie_f ('e', "pie_flex", [](int f, unsigned long t){   pie_flex.init(f, t);            }, TestInfo([](){ return pie_flex.test();            }, piezo_off, piezo_on),    [](){  pie_flex.del();       });
SensorInterface pie_h ('f', "pie_hard", [](int f, unsigned long t){   pie_hard.init(f, t);            }, TestInfo([](){ return pie_hard.test();            }, piezo_off, piezo_on),    [](){  pie_hard.del();       });
SensorInterface mic_i ('a', "mic"     , [](int f, unsigned long t){   init_mic(f, t);                 }, TestInfo([](){ return test_mic();                 }, mic_off,   mic_on  ),    [](){  del_mic();            });
SensorInterface acc_i ('c', "acc"     , [](int f, unsigned long t){   acc.init(f, t);                 }, TestInfo([](){ return acc.test();                 }, acc_off,   acc_on  ),    [](){  acc.del();            });
SensorInterface gyr_i ('d', "gyr"     , [](int f, unsigned long t){   gyr.init(f, t);                 }, TestInfo([](){ return gyr.test();                 }, acc_off,   acc_on  ),    [](){  gyr.del();            });
SensorInterface pro_i ('g', "pro"     , [](int f, unsigned long t){   pro.init(f, t);                 }, TestInfo([](){ return pro.test();                 }, prox_off,  prox_on ),    [](){  pro.del();            });
SensorInterface clu_i ('t', "Toggle Clutch", [](int f, unsigned long t){transform_init(f, t);         }, TestInfo([](){ return tranfrom_test();            }, 100,       200     ),    [](){  transfrom_delete();   });


short tmp1() {
  return 0;
}
void tmp2() {
  
}
SensorInterface cuc_i ('1', "uncouple", [](int f, unsigned long t){uncouple_servo();}, TestInfo(tmp1, 100, 200), tmp2);
SensorInterface cc_i  ('2', "couple",   [](int f, unsigned long t){couple_servo();  }, TestInfo(tmp1, 100, 200), tmp2);


// Combinations
TestInfo piezosTests[] = { 
                          TestInfo((TestFunction) [](){return pie_flex.test();}, piezo_off, piezo_on, 1),
                          TestInfo((TestFunction) [](){return pie_hard.test();}, piezo_off, piezo_on, 1)
};
SensorInterface piezos ('h', "piezos" , 
                        [](int f, unsigned long t){   pie_flex.init(f, t); pie_hard.init(f, t); }, 
                        piezosTests, 2, 1800,
                        [](){                         pie_flex.del()     ; pie_hard.del()     ; });

TestInfo piezo_imuTests[] = {
                          TestInfo((TestFunction) [](){return pie_hard.test();}, piezo_off, piezo_on, 1),
                          TestInfo((TestFunction) [](){return      acc.test();}, acc_off,   acc_on,   1)
};
SensorInterface piezos_imu ('i', "pie_hard/imu" , 
                        [](int f, unsigned long t){   pie_hard.init(f, t); acc.init(f, t); }, 
                        piezo_imuTests, 2, 1500,
                        [](){                         pie_hard.del()     ; acc.del()     ; });

TestInfo allTests[] = {
                          TestInfo((TestFunction) [](){return acc.test();      }, acc_off,   acc_on,   3),
                          TestInfo((TestFunction) [](){return pie_hard.test(); }, piezo_off, piezo_on, 2),
                          TestInfo((TestFunction) [](){return pro.test();      }, prox_off,  prox_on,  4),
                          TestInfo((TestFunction) [](){return test_mic();      }, mic_off,   mic_on,   0)
};
SensorInterface all ('j', "all", 
                        [](int f, unsigned long t){   acc.init(f, t); pie_hard.init(f, t); pro.init(f, t); init_mic(f, t); },
                        allTests, 4, 5000,
                        [](){              del_mic(); acc.del()     ; pie_hard.del()     ; pro.del()     ; });

TestInfo allTestsFusion[] = {
                          TestInfo((TestFunction) [](){return acc.test();      }, acc_off,   acc_on,   3),
                          TestInfo((TestFunction) [](){return pie_hard.test(); }, piezo_off, piezo_on, 2),
                          TestInfo((TestFunction) [](){return pro.test();      }, prox_off,  prox_on,  4)
};
SensorInterface fusion ('k', "fusion", 
                        [](int f, unsigned long t){   acc.init(f, t); pie_hard.init(f, t); pro.init(f, t);},
                        allTestsFusion, 3, 5000,
                        [](){              acc.del()     ; pie_hard.del()     ; pro.del()     ; });


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
  settings.addSensorInterface(&fusion);
  settings.addSensorInterface(&clu_i);
  settings.addSensorInterface(&cuc_i);
  settings.addSensorInterface(&cc_i);


  Serial.begin(115200);
  while(!Serial);

  pinMode(LED_BUILTIN, OUTPUT);
};

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
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
