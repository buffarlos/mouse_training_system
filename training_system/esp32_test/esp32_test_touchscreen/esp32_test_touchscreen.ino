#include "Adafruit_GFX.h"
#include "Adafruit_RA8875.h"

// Library only supports hardware SPI at this time
// Connect SCLK to ESP32-PROS3 Digital #36 (Hardware SPI clock)
// Connect MISO to ESP32-PROS3 Digital #37 (Hardware SPI MISO)
// Connect MOSI to ESP32-PROS3 Digital #35 (Hardware SPI MOSI)
#define RA8875_INT 9
#define RA8875_CS 34
#define RA8875_RESET 38

Adafruit_RA8875 tft = Adafruit_RA8875(RA8875_CS, RA8875_RESET);
uint16_t tx, ty;

void setup()
{
  Serial.begin(9600);
  Serial.println("RA8875 start");

  /* Initialize the display using 'RA8875_480x80', 'RA8875_480x128', 'RA8875_480x272' or 'RA8875_800x480' */
  // Test system display is 800x480, therefore init to 'RA8875_800x480'
  if (!tft.begin(RA8875_800x480)) {
    Serial.println("RA8875 Not Found!");
    while (1);
  }

  Serial.println("Found RA8875");

  tft.displayOn(true);
  tft.GPIOX(true);      // Enable TFT - display enable tied to GPIOX
  tft.PWM1config(true, RA8875_PWM_CLK_DIV1024); // PWM output for backlight
  tft.PWM1out(255);

  // With hardware acceleration this is instant
  tft.fillScreen(RA8875_WHITE);

  // Play with PWM
  for (uint8_t i=255; i!=0; i-=5 )
  {
    tft.PWM1out(i);
    delay(10);
  }
  for (uint8_t i=0; i!=255; i+=5 )
  {
    tft.PWM1out(i);
    delay(10);
  }
  tft.PWM1out(255);

  // Solid color screen fill
  tft.fillScreen(RA8875_RED);
  delay(500);
  tft.fillScreen(RA8875_YELLOW);
  delay(500);
  tft.fillScreen(RA8875_GREEN);
  delay(500);
  tft.fillScreen(RA8875_CYAN);
  delay(500);
  tft.fillScreen(RA8875_MAGENTA);
  delay(500);
  tft.fillScreen(RA8875_BLACK);

  // Try some GFX acceleration!
  // tft.drawCircle(100, 100, 50, RA8875_BLACK);
  // tft.fillCircle(100, 100, 49, RA8875_GREEN);

  // Draw rectangles for 5 choice
  tft.fillRect(70, 70, 100, 100, RA8875_WHITE);
  tft.fillRect(220, 70, 100, 100, RA8875_WHITE);
  tft.fillRect(370, 70, 100, 100, RA8875_WHITE);
  tft.fillRect(520, 70, 100, 100, RA8875_WHITE);
  tft.fillRect(670, 70, 100, 100, RA8875_WHITE);

  // tft.drawRect(10, 10, 400, 200, RA8875_GREEN);
  // tft.fillRoundRect(200, 10, 200, 100, 10, RA8875_RED);
  // tft.drawPixel(10,10,RA8875_BLACK);
  // tft.drawPixel(11,11,RA8875_BLACK);
  // tft.drawLine(10, 10, 200, 100, RA8875_RED);
  // tft.drawTriangle(200, 15, 250, 100, 150, 125, RA8875_BLACK);
  // tft.fillTriangle(200, 16, 249, 99, 151, 124, RA8875_YELLOW);
  // tft.drawEllipse(300, 100, 100, 40, RA8875_BLACK);
  // tft.fillEllipse(300, 100, 98, 38, RA8875_GREEN);
  // Argument 5 (curvePart) is a 2-bit value to control each corner (select 0, 1, 2, or 3)
  // tft.drawCurve(50, 100, 80, 40, 2, RA8875_BLACK);
  // tft.fillCurve(50, 100, 78, 38, 2, RA8875_WHITE);
  tft.drawChar(70, 200, 'C', RA8875_WHITE, RA8875_BLACK, 4);
  tft.drawChar(90, 200, 'a', RA8875_WHITE, RA8875_BLACK, 4);
  tft.drawChar(110, 200, 'r', RA8875_WHITE, RA8875_BLACK, 4);
  tft.drawChar(130, 200, 'l', RA8875_WHITE, RA8875_BLACK, 4);
  tft.drawChar(150, 200, 'o', RA8875_WHITE, RA8875_BLACK, 4);
  tft.drawChar(170, 200, 's', RA8875_WHITE, RA8875_BLACK, 4);

  pinMode(RA8875_INT, INPUT);
  digitalWrite(RA8875_INT, HIGH);

  tft.touchEnable(true);

  Serial.print("Status: "); Serial.println(tft.readStatus(), HEX);
  Serial.println("Waiting for touch events ...");
}

void loop()
{
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