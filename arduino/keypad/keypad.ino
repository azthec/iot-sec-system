#include <LiquidCrystal.h>
#include <SPI.h>
#include <WiFi.h>

// KEYPAD Globals
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
String lock_command = "AB";   // activation sequence
int key_position = 0;          // last input key position
int lock = true;

LiquidCrystal lcd (A0, A1, A2, A3, A4, A5);

// WIFI Globals

char ssid[] = "Carrinha SIS #42"; //  your network SSID (name)
char pass[] = "superpassword";    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;            // your network key Index number (needed only for WEP)

int status = WL_IDLE_STATUS;
char server[] = "192.168.43.244";    // name address for data server
int port = 8080;

WiFiClient client;


void setup() {

  // SERIAL Setup
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  Serial.println("Program starting"); 


  // KEYPAD Setup
  for(int i=0;i<4;i++) {
    pinMode(rpin[i],OUTPUT);
    pinMode(cpin[i],INPUT_PULLUP);
  }
  lcd.begin(16, 2);
  pinMode(redLED, OUTPUT);  //set the LED as an output
  pinMode(greenLED, OUTPUT);


  // WIFI Setup
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    while (true); // Stop here.
  }

  String fv = WiFi.firmwareVersion();
  if (fv != "1.1.0") {
    Serial.println("Please upgrade the firmware");
  }

  // Connect
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    delay(5000);
  }
  Serial.println("Connected to wifi");
  printWifiStatus();


  // Initial lock
  locked();
  
}
void loop() {
  char key=getkey();

  if(key==0) {
   
  } // keyboard has malfuctions with these keys
  else if(key == '7' || key == '8' || key == '9' ||
  key == '*' || key == '0' || key == '#' || key == 'C'){
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("  Invalid Key!");
    delay(200);
    lcd.clear();
  } else {
    if (key_position < 16) {
      if (key == 'D' && key_position >= 0) {
        input.remove(input.length() - 1, input.length());
        key_position--;
      } else if (key != 'D') {
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
    updateLock();
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

char getkey() {
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
    setLocked(true);
    send_locked();
    lcd.clear();
}

void send_locked() {
  char inChar;
  if (client.connect(server, port)) {
    Serial.println("Connected and sending lock request!");
    // Make a HTTP request:
    client.println("GET /?key=t7XodejIrK35NQSdklCIjM7fyeKIx2&source=keypad&value=1");
    client.print("Host: ");
    client.println(server);
    client.println("Connection: close");
    client.println();
  } else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("*** Unlocking ***");
    lcd.setCursor(0, 1);
    lcd.print("Connection fail!");
    Serial.println("Connection fail!");
    delay(3000);
    setLocked(false);
  }

  // if we don' read, even empty responses, eventually we run out of sockets...
  while(client.connected()) {
    while(client.available()) {
      inChar = client.read();
      Serial.write(inChar);
    }
  }

  Serial.println("Closing socket.");
  client.stop(); 
}

void unlocked() {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("*** Unlocking ***");
    delay(3000);
    setLocked(false);
    send_unlocked();
    lcd.clear();
}

void send_unlocked() {
  char inChar;
  if (client.connect(server, port)) {
    Serial.println("Connected and sending unlock request!");
    // Make a HTTP request:
    client.println("GET /?key=t7XodejIrK35NQSdklCIjM7fyeKIx2&source=keypad&value=0");
    client.print("Host: ");
    client.println(server);
    client.println("Connection: close");
    client.println();
  } else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("*** Locking ***");
    lcd.setCursor(0, 1);
    lcd.print("Connection fail!");
    Serial.println("Connection fail!");
    delay(3000);
    setLocked(true);
  }
  // if we don' read, even empty responses, eventually we run out of sockets...
  while(client.connected()) {
    while(client.available()) {
      inChar = client.read();
      Serial.write(inChar);
    }
  }

  Serial.println("Closing socket.");
  client.stop(); 
}

void setLocked(int locked){
  if(locked){
    digitalWrite(redLED, HIGH);
    digitalWrite(greenLED, LOW);
  } else{
    digitalWrite(redLED, LOW);
    digitalWrite(greenLED, HIGH);
  }
  lock = locked;
}

void updateLock() {
  if(lock){
    digitalWrite(redLED, HIGH);
    digitalWrite(greenLED, LOW);
  } else{
    digitalWrite(redLED, LOW);
    digitalWrite(greenLED, HIGH);
  }
}

void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}
