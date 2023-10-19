void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(A0, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available()>0) {
    char c = Serial.read();
    if(c=='s') {
      for(int i=0; i<2048; i++) {
        Serial.println(analogRead(A0));
      }
      Serial.println("e");
    } else {
      Serial.write(c);
    }
    
  }
}
