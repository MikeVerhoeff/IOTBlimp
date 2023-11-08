#pragma once

typedef short(*TestFunction)();

struct TestInfo {

  TestInfo(TestFunction function, short off, short on, short weight)
    : function(function), off(off), on(on), weight(weight) {}

  TestInfo(TestFunction function, short off, short on)
    : function(function), off(off), on(on), weight(1) {}
  
  TestInfo()
    : function(nullptr), off(0), on(0), weight(0) {}
  
  TestFunction function;
  short off;
  short on;
  short weight;
};

typedef struct TestInfo TestInfo;

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
