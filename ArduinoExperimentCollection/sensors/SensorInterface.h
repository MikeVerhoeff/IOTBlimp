#pragma once

float sigmoid_f(float x) {
  if(x < -1) {return 0;}
  if(x > 1 ) {return 1;}
  return (-(x-sqrt(3))*(x+sqrt(3))*x)/4+0.5;
}

float sigmoid_f(float off, float on, float x) {
  return sigmoid_f( (x - (on+off)/2) / (on-off) * 2 );
}

short sigmoid_s(short x)
{
  if (x < -1000) {return 0000;}
  if (x > 1000 ) {return 1000;}
  short x1 = x / 10;
  return -x1 * x1 * x1 / 4000 + 3 * x / 4 + 500;
}

short sigmoid_s(short off, short on, short x)
{
  return sigmoid_s( (x - (on+off)/2) * 2 * 1000 / (on-off) );
}

typedef short(*TestFunction)();

struct TestInfo {

  TestInfo(TestFunction function, short off, short on, short weight)
    : function(function), off(off), on(on), weight(weight) {}

  TestInfo(TestFunction function, short off, short on)
    : function(function), off(off), on(on), weight(1) {}

  // use on off 2
  TestInfo(TestFunction function, short off, short on, short on2, short off2, short weight)
    : function(function), off(off), on(on), on2(on2), off2(off2), useonoff2(true), weight(weight) {}

  TestInfo(TestFunction function, short off, short on, short on2, short off2)
    : function(function), off(off), on(on), on2(on2), off2(off2), useonoff2(true), weight(1) {}

  // default
  TestInfo()
    : function(nullptr), off(0), on(0), weight(0) {}
  
  TestFunction function;
  short off;
  short on;
  short on2 = 0;
  short off2 = 0;
  short weight;
  bool useonoff2 = false;

  unsigned long on_time = 0;
  unsigned long hold_time = 100000;
  short last_value = 0;
  bool used_last_value = false;

  void reset() {
    on_time = 0;
    last_value = 0;
    used_last_value = false;
  }
  
  short run(unsigned long current_time) {
    short v = function();
    //short tmp = v;
    if(useonoff2) {
      if(v < on2) {
        v = sigmoid_s(off, on, v);
      } else {
        v = sigmoid_s(off2, on2, v);
      }
    } else {
      v = sigmoid_s(off, on, v);
    }
    /*Serial.print(off);
    Serial.print(", ");
    Serial.print(on);
    Serial.print(", ");
    Serial.print(tmp);
    Serial.print(", ");
    Serial.println(v);*/
    v*= weight;
    
    bool in_hold_time = current_time - on_time < hold_time;
    
    bool value_larger = v>=last_value;

    if(value_larger) {
      last_value = v;
      on_time = current_time;
    }

    if(in_hold_time) {
      used_last_value = true;
      return last_value;
    }

    if (used_last_value) {
      used_last_value = false;
      last_value = v;
      on_time = current_time;
    }
    
    return v;
    
  }
};

typedef struct TestInfo TestInfo;

class SensorInterface {
private:
public:
  SensorInterface(char key, char* name, void (*init)(int, unsigned long), TestInfo functions[], short funcCount, short threshold, void (*del)())
  : key(key), name(name), init(init), funcCount(funcCount), del(del), threshold(threshold) {
    for(int i = 0; i<16 && i<funcCount; i++) {
       this->functions[i] = functions[i];
    }
  }

  SensorInterface(char key, char* name, void (*init)(int, unsigned long), TestInfo function, void (*del)())
  : key(key), name(name), init(init), del(del), functions({function}), funcCount(1), threshold(1000) {}
  
  char key;
  char* name;
  short threshold;
  void (*init)(int, unsigned long);
  void (*del)();
  short funcCount;
  TestInfo functions[16];
};
