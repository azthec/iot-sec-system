#include <LiquidCrystal.h>
#define redLED 10 //define the LED pins
#define greenLED 11

const char keymap[4][4]={
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
 };
const int rpin[]={9,8,7,6};
const int cpin[]={5,4,3,2};

String password = "1234";      // deactivation sequence
String input = "";             // user input string
String lock_command = "ABC";   // activation sequence
int key_position = 0;          // last input key position
int lock = true;

LiquidCrystal lcd (A0, A1, A2, A3, A4, A5);

void setup()
{
  Serial.begin(9600);
  Serial.println("Program starting"); 
  for(int i=0;i<4;i++)
  {
//Should be INPUT_PULLUP and OUTPUT
    pinMode(rpin[i],OUTPUT);
    pinMode(cpin[i],INPUT_PULLUP);
  }
  lcd.begin(16, 2);
  pinMode(redLED, OUTPUT);  //set the LED as an output
  pinMode(greenLED, OUTPUT);
  setLocked (true); //state of the password
}
void loop()
{
  char key=getkey();

  if(key==0) {
   
  } // keyboard has malfuctions with these keys
  else if(key == '7' || key == '8' || key == '9' ||
  key == '*' || key == '0' || key == '#'){
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("  Invalid Key!");
    delay(1000);
    lcd.clear();
  } else {
    if (key_position < 16) {
      if (key == 'D' && key_position >= 0) {
        input.remove(input.length() - 1, input.length());
        key_position--;
      } else {
        input.concat(key);
        key_position++;
      }
      Serial.print("K: ");
      Serial.println(key);
      Serial.print("I: ");
      Serial.println(input);
      if (input == password && lock) {
        unlocked();
        input = "";
        key_position = 0;
      } else if (input == lock_command && !lock) {
        locked();
        input = "";
        key_position = 0;
      }
      
    } else {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("   Invalid");
      lcd.setCursor(0, 1);
      lcd.print("  Sequence!");
      delay(1000);
      lcd.clear();
      input = "";
      key_position = 0;
      
    }
  }

  if (input.length() > 0) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("   User input:");
    lcd.setCursor(0, 1);
    lcd.print(input);
  } else if (!lock) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("    Welcome");
    lcd.setCursor(0, 1);
    lcd.print(" Alarm disabled!");
  } else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("    Welcome");
    lcd.setCursor(0, 1);
    lcd.print(" Alarm enabled!");
  }

  delay(200);              // Also, consider debouncing. 
}
char getkey()
{
  char key=0;
  for(int i=0;i<4;i++)
  {
    digitalWrite(rpin[i],LOW);
    for(int j=0;j<4;j++)
    {
      if (digitalRead(cpin[j])==LOW)
      key=keymap[i][j];
    }
    digitalWrite(rpin[i],HIGH);
  }
  return key;
}

void locked() {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("*** Locking ***");
    delay(3000);
    setLocked (true);
    lcd.clear();
}

void unlocked() {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("*** Unlocking ***");
    delay(3000);
    setLocked (false);
    lcd.clear();
}

void setLocked(int locked){
  if(locked){
    digitalWrite(redLED, HIGH);
    digitalWrite(greenLED, LOW);
    }
    else{
      digitalWrite(redLED, LOW);
      digitalWrite(greenLED, HIGH);
    }
    lock = locked;
  }
