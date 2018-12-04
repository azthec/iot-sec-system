const int PIEZO_PIN = A0; // Piezo output
const int SHARP_IR_PIN = A1; // Distance output


void setup() 
{
  Serial.begin(9600);
}

void loop() 
{
  // Read Piezo ADC value in, and convert it to a voltage
  int piezoADC = analogRead(PIEZO_PIN);
  float piezoV = piezoADC / 1023.0 * 5.0;
  if (piezoV > 0.05) {
    Serial.print("V: ");
    Serial.println(piezoV); // Print the voltage.
  }

   float volts = analogRead(SHARP_IR_PIN)*0.0048828125;  // value from sensor * (5/1024)
   int distance = 13*pow(volts, -1); // worked out from datasheet graph
   if (distance <= 30 && distance > 4) {
    Serial.print("D: ");
    Serial.println(distance); // Print the voltage.
  }
}
