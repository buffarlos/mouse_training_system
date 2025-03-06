/*
  training_system_firmware

  Firmware for mouse training system
*/

// ------------------------- Imports -------------------------
#include "Adafruit_GFX.h"
#include "Adafruit_RA8875.h"
#include <WiFi.h>
#include <esp_wifi.h>
#include <PubSubClient.h>

// ------------------------- Pin name definitions -------------------------
// Library only supports hardware SPI at this time
// Connect SCLK to ESP32-PROS3 Digital #36 (Hardware SPI clock)
// Connect MISO to ESP32-PROS3 Digital #37 (Hardware SPI MISO)
// Connect MOSI to ESP32-PROS3 Digital #35 (Hardware SPI MOSI)
#define RA8875_INT 9
#define RA8875_CS 34
#define RA8875_RESET 38
#define FEED_OP 12
#define MAG_OP 13
#define MAG_REP 42

// ------------------------- Constants -------------------------
const int choiceXPos[5] = {50, 200, 350, 500, 650};
const int choiceYPos = 330;
const int choiceSize = 100;
// Uncomment and fill with information before flashing
// const char* systemid = "mouse_1";
// const char* ssid = "";
// const char* password = "";
// const char* mqtt_server = "";

// ------------------------- Global variables -------------------------
char mac[17];
Adafruit_RA8875 tft = Adafruit_RA8875(RA8875_CS, RA8875_RESET);
uint16_t tx, ty;
WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

// ------------------------- Helper functions -------------------------
// Touchscreen helpers
void illuminateChoice(int choice) {
  tft.fillRect(
    choiceXPos[choice],
    choiceYPos,
    choiceSize,
    choiceSize,
    RA8875_WHITE
  );
}

bool checkChoiceTouch(int x, int y, int choice) {
  float xScale = 1024.0F/tft.width();
  float yScale = 1024.0F/tft.height();
  if (x/xScale > (choiceXPos[choice]) && x/xScale < (choiceXPos[choice] + choiceSize)
    && y/yScale > choiceYPos && y/yScale < (choiceYPos + choiceSize)) {
    return true;
  }
  return false;
}

void extinguishChoices() {
  for (int i = 0; i < 5; ++i) {
    tft.fillRect(
      choiceXPos[i],
      choiceYPos,
      choiceSize,
      choiceSize,
      RA8875_BLACK
    );
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

// MQTT helpers
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
      // Subscribe
      client.subscribe("esp32/output");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();

  if (String(topic) == "esp32/output") {
    Serial.print("Received command ");
    if(messageTemp == "on"){
      Serial.println("on");
      illuminateChoice(2);
    }
    else if(messageTemp == "off"){
      Serial.println("off");
      extinguishChoices();
    }
  }
}

// ------------------------- Training functions -------------------------

// ------------------------- Setup function -------------------------
void setup() {
  // Serial diagnostic communication begin
  Serial.begin(9600);

  // Screen initialization
  if (!tft.begin(RA8875_800x480)) {
    Serial.println("RA8875 Not Found!");
    while (1);
  }
  tft.displayOn(true);
  tft.GPIOX(true);      // Enable TFT - display enable tied to GPIOX
  tft.PWM1config(true, RA8875_PWM_CLK_DIV1024); // PWM output for backlight
  tft.PWM1out(255);
  tft.fillScreen(RA8875_BLACK);
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

  // Network initialization
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("\nConnecting");
  while(WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    delay(100);
  }
  Serial.println("\nConnected to the WiFi network");
    Serial.print("Local ESP32 IP: ");
    Serial.println(WiFi.localIP());

  // MQTT initialization
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

// ------------------------- Main loop -------------------------
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > 500) {
    lastMsg = now;
    client.publish("esp32/test", "ESP32 alive on network");
  }
}
