#include <SPI.h>
#include <WiFi.h>

// WIFI Globals

char ssid[] = "Carrinha SIS #42"; //  your network SSID (name)
char pass[] = "superpassword";    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;            // your network key Index number (needed only for WEP)

int status = WL_IDLE_STATUS;
char server[] = "192.168.43.244";    // name address for data server
int port = 8080;

WiFiClient client;
String key = "846HqXQ2xPD8TiMjTnshj0UETmxSpT";


// SENSOR Globals
const int analogInPin1 = A0; // Analog input pin that the Accelerometer's first pin is attached to
const int analogInPin2 = A1; // Analog input pin that the Accelerometer's second pin is attached to
int sensorValue1 = 0; // value read from the Accelerometer's first pin
int sensorValue2 = 0; // value read from the Accelerometer's second pin

const int SHARP_IR_PIN = A2; // Distance output

const int RunningAverageCount = 16;
float RunningAverageBuffer[RunningAverageCount];
int NextRunningAverage;

float raDistance;



// return the current time
float time() {
  return float( micros() ) * 1e-6;
}

float updateInterval = 15.0;
float lastUpdate = time();

void setup() {
  // SERIAL Setup
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  Serial.println("Program starting");

  // WIFI Setup
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    while (true); // Stop here.
  }

  String fv = WiFi.firmwareVersion();
  if (fv != "1.1.0") {
    Serial.println(fv);
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
}


int accelMaxDiff = 0;
int accelMaxDiffX;
int accelMaxDiffY;
float distanceMax = 0;

void loop() {
  // Read Piezo ADC value in, and convert it to a voltage
  sensorValue1 = analogRead(analogInPin1);
  sensorValue2 = analogRead(analogInPin2);
  // print the results to the serial monitor:

  accelMaxDiffX = max(abs(700 - sensorValue1), abs(500 - sensorValue1));
  accelMaxDiffY = max(abs(600 - sensorValue2), abs(400 - sensorValue2));

  if (accelMaxDiffX > accelMaxDiff) {
    accelMaxDiff = accelMaxDiffX;
  } else if (accelMaxDiffY > accelMaxDiff) {
    accelMaxDiff = accelMaxDiffY;
  }
  
   
  raDistance = getRADistance();
  if (raDistance > distanceMax && raDistance >= 3) {
    distanceMax = raDistance;
//    Serial.print("D: ");
//    Serial.println(raDistance);
  }
//
  if (time() > lastUpdate + updateInterval) {
//    
    lastUpdate = time();
    sendHTTPUpdate(key, "distance", distanceMax);
    sendHTTPUpdate(key, "movement", accelMaxDiff);
//    Serial.println(accelMaxDiff);
//    Serial.println(distanceMax);
    distanceMax = 0;
    accelMaxDiff = 0;
  }

}


float getRADistance() {
    float volts = analogRead(SHARP_IR_PIN)*0.0048828125;  // value from sensor * (5/1024)
    int distance = 13*pow(volts, -1); // worked out from datasheet graph
    
    RunningAverageBuffer[NextRunningAverage++] = distance;
    if (NextRunningAverage >= RunningAverageCount) {
      NextRunningAverage = 0; 
    }
    float RunningAverageDistance = 0;
    for(int i=0; i< RunningAverageCount; ++i) {
      RunningAverageDistance += RunningAverageBuffer[i];
    }
    return RunningAverageDistance /= RunningAverageCount;
}


void sendHTTPUpdate(String key, String source, float value) {
  char inChar;
  if (client.connect(server, port)) {
    Serial.println("Sending distance update!");
    // Make a HTTP request:
    client.print("GET /?key=");
    client.print(key);
    client.print("&source=");
    client.print(source);
    client.print("&value=");
    client.println(value);
    client.print("Host: ");
    client.println(server);
    // client.println("Connection: close");
    client.println();
  } else {
    Serial.println("Connection Failed.");
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
