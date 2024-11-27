/*
  training_system_firmware

  Firmware for mouse training system
*/

// ------------------------- Imports -------------------------
#include "Adafruit_GFX.h"
#include "Adafruit_RA8875.h"

// ------------------------- Pin name definitions -------------------------
// Library only supports hardware SPI at this time
// Connect SCLK to ESP32-PROS3 Digital #36 (Hardware SPI clock)
// Connect MISO to ESP32-PROS3 Digital #37 (Hardware SPI MISO)
// Connect MOSI to ESP32-PROS3 Digital #35 (Hardware SPI MOSI)
#define RA8875_INT 9
#define RA8875_CS 34
#define RA8875_RESET 38

Adafruit_RA8875 tft = Adafruit_RA8875(RA8875_CS, RA8875_RESET);
uint16_t tx, ty;

// ------------------------- Helper functions -------------------------

// ------------------------- Setup function -------------------------
void setup() {
  if (!tft.begin(RA8875_800x480)) {
    Serial.println("RA8875 Not Found!");
    while (1);
  }

  tft.displayOn(true);
  tft.GPIOX(true);      // Enable TFT - display enable tied to GPIOX
  tft.PWM1config(true, RA8875_PWM_CLK_DIV1024); // PWM output for backlight
  tft.PWM1out(255);

  tft.fillScreen(RA8875_WHITE);

  tft.drawChar(70, 200, 'C', RA8875_BLACK, RA8875_WHITE, 3);
  tft.drawChar(90, 200, 'a', RA8875_BLACK, RA8875_WHITE, 3);
  tft.drawChar(110, 200, 'r', RA8875_BLACK, RA8875_WHITE, 3);
  tft.drawChar(130, 200, 'l', RA8875_BLACK, RA8875_WHITE, 3);
  tft.drawChar(150, 200, 'o', RA8875_BLACK, RA8875_WHITE, 3);
  tft.drawChar(170, 200, 's', RA8875_BLACK, RA8875_WHITE, 3);

  pinMode(RA8875_INT, INPUT);
  digitalWrite(RA8875_INT, HIGH);

  tft.touchEnable(true);
}

// ------------------------- Main loop -------------------------
void loop() {
  float xScale = 1024.0F/tft.width();
  float yScale = 1024.0F/tft.height();

  /* Wait around for touch events */
  if (! digitalRead(RA8875_INT))
  {
    if (tft.touched())
    {
      Serial.print("Touch: ");
      tft.touchRead(&tx, &ty);
      Serial.print(tx); Serial.print(", "); Serial.println(ty);
      /* Draw a circle */
      tft.fillCircle((uint16_t)(tx/xScale), (uint16_t)(ty/yScale), 4, RA8875_GREEN);
    }
  }
}
