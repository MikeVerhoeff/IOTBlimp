#pragma once

class SensorInterface {
private:
public:
  SensorInterface(char key, char* name, void (*init)(int, unsigned long), void (*function)(), void (*del)()) : key(key), name(name), init(init), function(function), del(del) {}
  
  char key;
  char* name;
  void (*init)(int, unsigned long);
  void (*function)();
  void (*del)();
};
