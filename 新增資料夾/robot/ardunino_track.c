// 改造伺服馬達的部分可參考影片
// https://youtu.be/4Pouf9iWLns

#include <Servo.h>

//////////////動作參數設定//////////////
int moveSmooth = 25; //兩個動作之間的平滑參數
int stepTime = 100;   //到定點之後停留的時間
//////////////////////////////////////


//////////////各零件腳位設定////////////
//伺服馬達腳位
int servopinA = 6;
int servopinB = 7;
int servopinC = 8;
int servopinD = 9;

//伺服馬達訊號回傳腳位
int sensorpinA = A0;
int sensorpinB = A1;
int sensorpinC = A2;
int sensorpinD = A3;

// LED燈腳位
int RLedPin = 5;
int GLedPin = 15;
int BLedPin = 14;

// 按鈕腳位
int ButtonA = 10;
int ButtonB = 16;
//////////////////////////////////////

//馬達校正基準點
int regulateMin = 70 ; 
int regulateMax = 110 ;

int posCount = 100;
int POS [100][4] ; //最多可紀錄100組手臂狀態

int ServoPosA = 90; //轉動角度
int ServoPosB = 90; //轉動角度
int ServoPosC = 90; //轉動角度
int ServoPosD = 90; //轉動角度

int sensorMaxA , sensorMaxB, sensorMaxC, sensorMaxD ; //紀錄可變電阻最大值
int sensorMinA , sensorMinB, sensorMinC, sensorMinD ; //紀錄可變電阻最小值

Servo servoA;
Servo servoB;
Servo servoC;
Servo servoD;

int arrayCount = 0;
int clearPos = 0;

//所有馬達連接
void MotorON() {
  servoA.attach(servopinA);
  servoB.attach(servopinB);
  servoC.attach(servopinC);
  servoD.attach(servopinD);
}

//所有馬達斷開連接
void MotorOFF() {
  servoA.detach();
  servoB.detach();
  servoC.detach();
  servoD.detach();
}

void setup() { 

  pinMode(RLedPin, OUTPUT);
  pinMode(GLedPin, OUTPUT);
  pinMode(BLedPin, OUTPUT);

  digitalWrite(GLedPin, HIGH);

  //先轉到90度
  MotorON();
  servoA.write(ServoPosA);
  servoB.write(ServoPosB);
  servoC.write(ServoPosC);
  servoD.write(ServoPosD);
  delay(500);

  //偵測小角度基準數值
  servoA.write(regulateMin);
  servoB.write(regulateMin);
  servoC.write(regulateMin);
  servoD.write(regulateMin);
  delay(1500);
  MotorOFF();
  delay(100);
  sensorMinA = analogRead(sensorpinA);
  sensorMinB = analogRead(sensorpinB);
  sensorMinC = analogRead(sensorpinC);
  sensorMinD = analogRead(sensorpinD);

  //偵測大角度基準數值
  MotorON();
  servoA.write(regulateMax);
  servoB.write(regulateMax);
  servoC.write(regulateMax);
  servoD.write(regulateMax);
  delay(1500);
  MotorOFF();
  delay(100);
  sensorMaxA = analogRead(sensorpinA);
  sensorMaxB = analogRead(sensorpinB);
  sensorMaxC = analogRead(sensorpinC);
  sensorMaxD = analogRead(sensorpinD);

  //轉到90度起始位置
  MotorON();
  servoA.write(ServoPosA);
  servoB.write(ServoPosB);
  servoC.write(ServoPosC);
  servoD.write(ServoPosD);
  delay(500);

  MotorOFF();

  pinMode(ButtonA, INPUT_PULLUP);
  pinMode(ButtonB, INPUT_PULLUP);
}


void loop() { // put your main code here, to run repeatedly:

//紀錄按鈕
  if (digitalRead(ButtonA) == LOW) 
  {
    digitalWrite(RLedPin, HIGH);
    digitalWrite(GLedPin, LOW);
    //清零arraycount
    if (clearPos == 1) {
      arrayCount = 0;
      clearPos = 0;
    }
    MotorOFF();
    delay(100);
    
    //將讀取到的數值，轉換成伺服馬達角度
    ServoPosA = map(analogRead(sensorpinA), sensorMinA, sensorMaxA, regulateMin, regulateMax);
    ServoPosB = map(analogRead(sensorpinB), sensorMinB, sensorMaxB, regulateMin, regulateMax);
    ServoPosC = map(analogRead(sensorpinC), sensorMinC, sensorMaxC, regulateMin, regulateMax);
    ServoPosD = map(analogRead(sensorpinD), sensorMinD, sensorMaxD, regulateMin, regulateMax);

    if (arrayCount < posCount) {
      POS[arrayCount][0] = ServoPosA;
      POS[arrayCount][1] = ServoPosB;
      POS[arrayCount][2] = ServoPosC;
      POS[arrayCount][3] = ServoPosD;
      arrayCount++;
    } else {
      for (int i = 0; i < 10; i++) {
        digitalWrite(RLedPin, HIGH);
        delay(100);
        digitalWrite(RLedPin, LOW);
        delay(100);
      }
      //?
      arrayCount = posCount - 1;
    }
    delay(200);
    digitalWrite(RLedPin, LOW);
    digitalWrite(GLedPin, HIGH);
  }

//播放按鈕
  if (digitalRead(ButtonB) == LOW) {
    digitalWrite(BLedPin, HIGH);
    digitalWrite(GLedPin, LOW);
    MotorON();
    servoA.write(POS[0][0]);
    servoB.write(POS[0][1]);
    servoC.write(POS[0][2]);
    servoD.write(POS[0][3]);
    delay(1000);

    for (int i = 0; i < arrayCount - 1; i++) {//i < arrayCount - 1?
      int POSNowA = POS[i][0];
      int POSNowB = POS[i][1];
      int POSNowC = POS[i][2];
      int POSNowD = POS[i][3];
      int POSGoalA = POS[i + 1][0];
      int POSGoalB = POS[i + 1][1];
      int POSGoalC = POS[i + 1][2];
      int POSGoalD = POS[i + 1][3];

      for (int j = 0; j < moveSmooth; j++) {//j < moveSmooth 可改為j <= moveSmooth
        servoA.write(map(j, 0, moveSmooth, POSNowA, POSGoalA));
        servoB.write(map(j, 0, moveSmooth, POSNowB, POSGoalB));
        servoC.write(map(j, 0, moveSmooth, POSNowC, POSGoalC));
        servoD.write(map(j, 0, moveSmooth, POSNowD, POSGoalD));
        delay(10);
      }
      delay(stepTime);
    }
    delay(500);
    clearPos = 1;
    MotorOFF();
    digitalWrite(BLedPin, LOW);
    digitalWrite(GLedPin, HIGH);
  }

}