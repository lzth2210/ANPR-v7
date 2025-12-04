#include <Servo.h>

Servo myServo;

int LED1 = 2;
int LED2 = 3;
int LED3 = 4;
int LED4 = 5;
int LED5 = 6;
int LED6 = 7;
int LEDred = 11;
int LEDblue = 10;
int LEDgreen = 9;
int option;

void setup() {
  Serial.begin(9600);
    pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  pinMode(LED4, OUTPUT);
  pinMode(LED5, OUTPUT);
  pinMode(LED6, OUTPUT);
  pinMode(LEDred, OUTPUT);
  pinMode(LEDblue, OUTPUT);
  pinMode(LEDgreen, OUTPUT);
  myServo.attach(8);
}

void loop() {
  if(Serial.available() > 0){
    option = Serial.read();
    Serial.println(option);
    if(option == 'R'){
      digitalWrite(LEDred, HIGH);
      digitalWrite(LEDblue, LOW);
      digitalWrite(LEDgreen, LOW);
      myServo.write(0);
    }
    if(option == 'V'){
      digitalWrite(LEDred, LOW);
      digitalWrite(LEDblue, LOW);
      digitalWrite(LEDgreen, HIGH);
      myServo.write(90);
    }
    if(option == 'A'){
        digitalWrite(LED1, HIGH);
    }
    if(option == 'B'){
        digitalWrite(LED2, HIGH);
    }
    if(option == 'C'){
        digitalWrite(LED3, HIGH);
    }
    if(option == 'D'){
        digitalWrite(LED4, HIGH);
    }
    if(option == 'E'){
        digitalWrite(LED5, HIGH);
    }
    if(option == 'F'){
        digitalWrite(LED6, HIGH);
    }
    if(option == 'G'){
        digitalWrite(LED1, LOW);
    }
    if(option == 'H'){
        digitalWrite(LED2, LOW);
    }
    if(option == 'I'){
        digitalWrite(LED3, LOW);
    }
    if(option == 'J'){
        digitalWrite(LED4, LOW);
    }
    if(option == 'K'){
        digitalWrite(LED5, LOW);
    }
    if(option == 'L'){
        digitalWrite(LED6, LOW);
    }
  }
}
    