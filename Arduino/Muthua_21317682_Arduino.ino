// Serial communication setup
constexpr long serial_baud_rate = 19200;
constexpr auto serial_config = SERIAL_8E1;

// Leonardo board information
constexpr int digital_pins[] = {9, 10, 11};
constexpr int analogue_pins[] = {A0, A1, A2};

// Frequency modes for TIMER1
#define PWM62k   1   //62500 Hz
#define PWM8k    2   // 7812 Hz
#define PWM1k    3   //  976 Hz
#define PWM244   4   //  244 Hz
#define PWM61    5   //   61 Hz

// Direct PWM change variables
#define PWM11  OCR1C

// Configure the PWM clock
// The argument is one of the 5 previously defined modes
void pwm91011configure(int mode)
{
// TCCR1A configuration
//  00 : Channel A disabled D9
//  00 : Channel B disabled D10
//  00 : Channel C disabled D11
//  01 : Fast PWM 8 bit
TCCR1A=1;

// TCCR1B configuration
// Clock mode and Fast PWM 8 bit
TCCR1B=mode|0x08;  

// TCCR1C configuration
TCCR1C=0;
}

// Set PWM to D11
// Argument is PWM between 0 and 255
void pwmSet11(int value)
{
OCR1C=value;   // Set PWM value
DDRB|=1<<7;    // Set Output Mode B7
TCCR1A|=0x08;  // Set PWM value
}

// Macro to converts from duty (0..100) to PWM (0..255)
#define DUTY2PWM(x)  ((255*(x))/100)



const String STUDENT_NUMBER = "21317682";

unsigned long time1 = millis(); // LED receive indicator timer
unsigned long time2 = millis(); // Debug mode timer
unsigned long MillisecondsUpdtime = 0; // Uptime Counter
unsigned long time3 = millis(); //Instantaneous data timer
unsigned long time_reset;
boolean reset = 0;

const byte numChars = 3; // two read bytes + end-of-line
char receivedChars[numChars]; // an array to store the received data

boolean newData = false;
boolean DebugMode = false;

String BinaryString = "";
String Outputstring = "";
int Aread = 0;
int value = 0;

void setup() {
 Serial.begin(19200,serial_config);
 pinMode(digital_pins[0], OUTPUT);
 pinMode(digital_pins[1], INPUT);
 pinMode(digital_pins[2], OUTPUT);

 // Generate PWM at pin 11 with 30% duty
// We need to call pwm91011configure before
// We use here the DUTY2PWM macro
pwm91011configure(PWM8k);
pwmSet11(175);
}

void loop() 
{
 ReceiveData();
 TransmitData();
 InstantData();
 DebugCheck();
 TripReset();
 
 // LED receive notifier timeout
 if(millis()-time1 > 200) {
    digitalWrite(LED_BUILTIN, LOW);  
    time1 = millis(); }
    
 PWM11=value;
value=140;

}



void ReceiveData() {
  
 char Read_end = '\n';
 static byte rdx = 0;
 char ReadCharacter;
 

 while (Serial.available() > 0 && newData == false) {
  
  ReadCharacter = Serial.read();
 
  digitalWrite(LED_BUILTIN, HIGH); 
 
  if (ReadCharacter != Read_end) {
    receivedChars[rdx] = ReadCharacter;
    rdx++;
    if (rdx >= numChars) {
      rdx = numChars - 1;
    }
  }
  else {
    receivedChars[rdx] = '\0'; // terminate the string
    rdx = 0;
    newData = true;
    }
  }
}

void TransmitData(){
  if (newData == true){
    if (receivedChars[0] == '0' && DebugMode == false){
        Serial.println(receivedChars[0]);
        Serial.println(STUDENT_NUMBER);
    }
    if (receivedChars[0] == '1' && DebugMode == false){
     Serial.println(receivedChars[0]);
     Serial.println(receivedChars[1]);
		 //Here you can apply calibration as necessary. 
		 switch (receivedChars[1]) {      
			 case '0' : 
			    Aread = (float)analogRead(analogue_pins[0]);
          Aread = (Aread/1024)*5;
          Aread = 4.01*Aread +10.4;
          Aread = Aread/1.4142;
          break;
       case '1' : 
          Aread = (float)analogRead(analogue_pins[1]);
          Aread = (Aread/1024)*5;
          Aread = 68.1*Aread +2.14;
          Aread = Aread/1.4142;
          break;
			 case '2' : 
			    Aread = (float)analogRead(analogue_pins[2]);
          Aread = (Aread/1024)*5;
          Aread = 68.1*Aread +2.14; 
          break;
     }
    
    
  	Serial.println(Aread);
    }
    if (receivedChars[0] == '2' && DebugMode == false){
      Serial.println(receivedChars[0]);
      Serial.println(receivedChars[1]);
		switch (receivedChars[1]) {
			case '0' : Serial.println(digitalRead(digital_pins[0])); break;
      case '1' : Serial.println(digitalRead(digital_pins[1])); break;
			case '2' : Serial.println(digitalRead(digital_pins[2])); break;
    }
  }
 	if (receivedChars[0] == 'x' || receivedChars[0] == 'X'){
         if (receivedChars[1] == '0'){
            DebugMode = false;
         }
         else if (receivedChars[1] == '1'){
            DebugMode = true;
         }
    }

   if ((receivedChars[0] == 'U') && DebugMode == false) // Return uptime if '?' is received
     {
       MillisecondsUpdtime=millis(); 
       uptime(); 
     }

    if ((receivedChars[0] == 'R')) // Trip reset
     {
      time_reset = millis();
      digitalWrite(digital_pins[0],HIGH);
      reset = 1;
     }
 }
  newData = false;
}

void TripReset(){
   if(millis()-time_reset > 100) {
    reset = 0;
    digitalWrite(digital_pins[0], LOW);  
    time_reset = millis(); }
}

void InstantData(){
  if(DebugMode==false){
    if(millis()-time3 > 500){
      //float v = (float)analogRead(analogue_pins[0]);
      //Serial.println((((float)(((v)/1024)*(5/5.6))+(5/11))*23));
      //Serial.println((((float)((((float)analogRead(analogue_pins[1]))/1024)*5)/14.6445)*1000));
      //Serial.println(((float)((((float)analogRead(analogue_pins[2]))/1024)*5)/0.08712));
      float voltage_read = (float)analogRead(analogue_pins[0]);
      voltage_read = (voltage_read/1024)*5;
      voltage_read = 4.01*voltage_read +10.4;
      float current_read = (float)analogRead(analogue_pins[1]);
      current_read = (current_read/1024)*5;
      current_read = 68.1*current_read +2.14;
      float phase_read = (float)analogRead(analogue_pins[2]);
      phase_read = (phase_read/1024)*5;
      phase_read = 12.1*phase_read +0.448;
      Serial.println(voltage_read/1.4142);
      Serial.println(round(current_read/1.4142));
      Serial.println(round(phase_read));
       Serial.println(digitalRead(digital_pins[0]));
       Serial.println(digitalRead(digital_pins[1]));
       Serial.println(digitalRead(digital_pins[2]));
       time3 = millis();
    }
  }
}

void DebugCheck(){
  if (DebugMode == true){
          String DebugOutput = "";
          int Aread0 = analogRead(analogue_pins[0]);
          delay(10);
          int Aread1 = analogRead(analogue_pins[1]);
          delay(10);
          int Aread2 = analogRead(analogue_pins[2]);
          delay(10);
          DebugOutput = STUDENT_NUMBER + ',' + "A0:" + Aread0 + ',' + "A1:" + Aread1 + ',' + "A2:" + Aread2 + 
          ',' + "D0:" + ReturnDigitalRead(digitalRead(digital_pins[0])) + ',' + "D1:" + ReturnDigitalRead(digitalRead(digital_pins[1])) + 
          ',' + "D2:" + ReturnDigitalRead(digitalRead(digital_pins[2]));
          if(millis()-time2 > 2000) { // LED receive notifier timeout 
            Serial.println(DebugOutput);
            time2 = millis(); }
       }
}

String ReturnDigitalRead(int Input){
  if (Input == 0){
    return "LOW";
  }
  else {
    return "HIGH";
  }
}



void uptime()
{
 long days=0;
 long hours=0;
 long mins=0;
 long secs=0;
 secs = MillisecondsUpdtime/1000; //convect milliseconds to seconds
 mins=secs/60; //convert seconds to minutes
 hours=mins/60; //convert minutes to hours
 days=hours/24; //convert hours to days
 secs=secs-(mins*60); //subtract the coverted seconds to minutes in order to display 59 secs max
 mins=mins-(hours*60); //subtract the coverted minutes to hours in order to display 59 minutes max
 hours=hours-(days*24); //subtract the coverted hours to days in order to display 23 hours max
 //Display results
 Serial.print("Uptime : ");
 Serial.print(hours);
 Serial.print(":");
 Serial.print(mins);
 Serial.print(":");
 Serial.println(secs);
}
 
