#pragma once

class SensorInterface {
private:
public:
  SensorInterface(char key, char* name, void (*function)()) : key(key), name(name), function(function) {}
  
  char key;
  char* name;
  void (*function)();
};
