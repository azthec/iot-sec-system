#include "Keypad.h"
const byte ROWS = 4; // four rows
const byte COLS = 3; // three columns
char keys[ROWS][COLS] =
{
{'1','2','3' },
{'4','5','6' },
{'7','8','9' },
{'*','0','#' }
};
byte rowPins[ROWS] = {5, 6, 7, 8};
byte colPins[COLS] = {2, 3, 4};
Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS );
char KEY[4] = {'1','2','3','4'}; // default secret key
char attempt[4] = {0,0,0,0};
int z=0;
void setup() {
   Serial.begin(9600);
}

void readKeypad() {
   char key = keypad.getKey();
   if (key != NO_KEY)
   {
    Serial.println(key);
   }
}
void loop()
{
   readKeypad();
}
