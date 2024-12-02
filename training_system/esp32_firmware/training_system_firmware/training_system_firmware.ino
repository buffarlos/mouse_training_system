/*
  training_system_firmware

  Firmware for mouse training system
*/

// ------------------------- Imports -------------------------
#include "Adafruit_GFX.h"
#include "Adafruit_RA8875.h"
#include <WiFi.h>
#include <esp_wifi.h>

// ------------------------- Pin name definitions -------------------------
// Library only supports hardware SPI at this time
// Connect SCLK to ESP32-PROS3 Digital #36 (Hardware SPI clock)
// Connect MISO to ESP32-PROS3 Digital #37 (Hardware SPI MISO)
// Connect MOSI to ESP32-PROS3 Digital #35 (Hardware SPI MOSI)
#define RA8875_INT 9
#define RA8875_CS 34
#define RA8875_RESET 38

// ------------------------- Global variables -------------------------
char mac[17];
char defaultMac[] = "Default MAC Address: ";
char getMacFail[] = "Failed to get MAC Address";
Adafruit_RA8875 tft = Adafruit_RA8875(RA8875_CS, RA8875_RESET);
uint16_t tx, ty;

// ------------------------- Helper functions -------------------------
bool getMacAddress(){
  uint8_t baseMac[6];
  char macAddress[17];
  esp_err_t ret = esp_wifi_get_mac(WIFI_IF_STA, baseMac);
  if (ret == ESP_OK) {
    for (int i = 0; i < 6; ++i) {
      int n = baseMac[i];
      char hex[2] = {'0', '0'};
      int index = 0;
      if (n > 255 || n < 0) {
        char invalidMac[] = "Invalid MAC address";
        return false;
      }
      while (n != 0) {
        int rem = 0;
        char ch;
        rem = n % 16;
        if (rem < 10) {
          ch = rem + 48;
        }
        else {
          ch = rem + 55;
        }
        hex[index] = ch;
        n = n/16;
        index += 1;
      }
      macAddress[i*3] = hex[1];
      macAddress[i*3 + 1] = hex[0];
      if (i < 5) {
        macAddress[i*3 + 2] = ':';
      }
    }
    for (int i = 0; i < 17; ++i) {
      mac[i] = macAddress[i];
    }
    return true;
  }
  else {
    return false;
  }
}

void illuminateChoice(int choice) {
  tft.fillRect(50 + choice*150, 330, 100, 100, RA8875_WHITE);
}

bool checkChoiceTouch(int x, int y, int choice) {
  float xScale = 1024.0F/tft.width();
  float yScale = 1024.0F/tft.height();
  if (x/xScale > (50 + choice*150) && x/xScale < (150 + choice*150)
    && y/yScale > 330 && y/yScale < 430) {
    return true;
  }
  return false;
}

void extinguishChoices() {
  for (int i = 0; i < 5; ++i) {
    tft.fillRect(50 + i*150, 330, 100, 100, RA8875_BLACK);
  }
}

void printToScreen(int startx, int starty, char text[], uint16_t color, uint16_t bg, uint8_t size) {
  int length = strlen(text);
  Serial.println(strlen(text));
  Serial.println(text);
  int characterWidth = size*6;
  for (int i = 0; i < length; ++i) {
    tft.drawChar(startx + characterWidth*i, starty, text[i], color, bg, size);
  }
}

// ------------------------- Training functions -------------------------
void fiveCSRTConstantInterval() {
  while (true) {
    Serial.println("==== 5CSRT Constant Interval ====");
    int choice = random(0, 5);
    illuminateChoice(choice);
    unsigned long start = millis();
    while (true) {
      if (! digitalRead(RA8875_INT)) {
        if (tft.touched()) {
          tft.touchRead(&tx, &ty);
          if (checkChoiceTouch(tx, ty, choice)) {
            unsigned long latency = millis() - start;
            Serial.print("Correct response in ");
            Serial.print(latency);
            Serial.println(" milliseconds");
            extinguishChoices();
            break;
          }
          else {
            unsigned long latency = millis() - start;
            Serial.print("Incorrect response in ");
            Serial.print(latency);
            Serial.println(" milliseconds");
            extinguishChoices();
            break;
          }
        }
      }
      if (millis() - start > 2000) {
        Serial.println("Task timed out after 2 seconds");
        extinguishChoices();
        break;
      }
    }
    // Debounce grace period
    delay(500);
    tft.touchRead(&tx, &ty);
  }
}

// ------------------------- Setup function -------------------------
void setup() {
  Serial.begin(9600);

  if (!tft.begin(RA8875_800x480)) {
    Serial.println("RA8875 Not Found!");
    while (1);
  }

  tft.displayOn(true);
  tft.GPIOX(true);      // Enable TFT - display enable tied to GPIOX
  tft.PWM1config(true, RA8875_PWM_CLK_DIV1024); // PWM output for backlight
  tft.PWM1out(255);

  tft.fillScreen(RA8875_BLACK);

  WiFi.mode(WIFI_STA);
  WiFi.STA.begin();

  Serial.print(defaultMac);
  bool macSuccess = getMacAddress();
  if (macSuccess) {
    Serial.println(mac);
    printToScreen(70,70, mac, RA8875_WHITE, RA8875_BLACK, 3);
  }
  else {
    Serial.println(getMacFail);
  }

  illuminateChoice(0);
  illuminateChoice(1);
  illuminateChoice(2);
  illuminateChoice(3);
  illuminateChoice(4);
  delay(1000);
  extinguishChoices();

  pinMode(RA8875_INT, INPUT);
  digitalWrite(RA8875_INT, HIGH);

  tft.touchEnable(true);
}

// ------------------------- Main loop -------------------------
void loop() {
  fiveCSRTConstantInterval();
}
