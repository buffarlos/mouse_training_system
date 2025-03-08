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
// Touchscreen library only supports hardware SPI at this time
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
// 5 choice location and size information
const int choiceXPos[5] = {50, 200, 350, 500, 650};
const int choiceYPos = 330;
const int choiceSize = 100;
// Reward parameters
const int pumpFlowRate = 1; // milliliters per second
const int rewardVolume = 2; // milliliters
/*
###################################################
### Network params - fill with info, then flash ###
###################################################
*/
// const char* subjectID = "";
// const char* ssid = "";
// const char* password = "";
// const char* mqttServer = "";

// ------------------------- Global variables -------------------------
// Touchscreen
Adafruit_RA8875 tft = Adafruit_RA8875(RA8875_CS, RA8875_RESET);
uint16_t tx, ty;
// Network
char topicSub[30];
char topicPub[30];
WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
char outgoingMsg[100];
int value = 0;
unsigned long lastCentralComputerPing = 0;

// ------------------------- Helper functions -------------------------
// Touchscreen helpers
/**
  * @brief Illuminates touchscreen choice passed to this function
  *
  * Given a 5 choice selection passed to this function, the function will
  * illuminate it on the touchscreen based on defined 5 choice position
  * parameters.
  *
  * @param choice: Which 5 choice selection to illuminate on screen
  */
void illuminateChoice(int choice) {
  tft.fillRect(
    choiceXPos[choice],
    choiceYPos,
    choiceSize,
    choiceSize,
    RA8875_WHITE
  );
}

/**
  * @brief Checks if touchscreen choice passed to this function is touched
  * based on touch coordinates passed
  *
  * Given a 5 choice selection passed to this function, the function will
  * check whether it has been touched based on defined 5 choice position
  * parameters and touch coordinates.
  *
  * @param x: Touch x coordinate
  * @param y: Touch y coordinate
  * @param choice: Which 5 choice selection to check if touched
  *
  * @return true if choice touched, false otherwise
  */
bool checkChoiceTouch(int x, int y, int choice) {
  float xScale = 1024.0F/tft.width();
  float yScale = 1024.0F/tft.height();
  if (x/xScale > (choiceXPos[choice]) && x/xScale < (choiceXPos[choice] + choiceSize)
    && y/yScale > choiceYPos && y/yScale < (choiceYPos + choiceSize)) {
    return true;
  }
  return false;
}

/**
  * @brief Extinguishes all 5 choices
  *
  * This function extinguishes all 5 choices on the touchscreen by drawing over them
  * with black squares.
  */
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
/**
  * @brief Attempts to connect to MQTT network if not connected
  *
  * This function will attempt to connect to the MQTT network if currently disconnected.
  */
void reconnect() {
  // Loop until reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
      // Subscribe
      client.subscribe(topicSub);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

/**
  * @brief Interprets incoming MQTT messages
  *
  * This function is invoked when an MQTT message arrives on the subscribed topic.
  * In turn, this function invokes the appropriate training function based on the
  * message contents.
  */
void callback(char* topic, byte* message, unsigned int length) {
  String messageTemp;
  if (String(topic) == topicSub) {
    Serial.print("Message arrived on topic: ");
    Serial.print(topic);
    Serial.print(". Message: ");
    for (int i = 0; i < length; i++) {
      Serial.print((char)message[i]);
      messageTemp += (char)message[i];
    }
    Serial.println();
    // Place all central computer commands here!
    if (messageTemp == "hab1") {
      hab1();
    }
    else if (messageTemp == "hab2") {
      hab2();
    }
    else if (messageTemp == "5csr_citi_10") {
      fiveChoice(10000, 4000);
    }
    else if (messageTemp == "5csr_citi_8") {
      fiveChoice(8000, 4000);
    }
    else if (messageTemp == "5csr_citi_4") {
      fiveChoice(4000, 4000);
    }
    else if (messageTemp == "5csr_citi_2") {
      fiveChoice(2000, 4000);
    }
    else if (messageTemp == "5csr_viti") {
      unsigned long interTrialDuration = random(2, 7);
      interTrialDuration = interTrialDuration*1000;
      fiveChoice(2000, interTrialDuration);
    }
  }
}

// ------------------------- Training functions -------------------------
/**
  * @brief Operates the feeder magazine
  *
  * When invoked, this function checks the reward parameter to determine whether
  * a food reward should be administered. Then, it will illuminate the magazine to
  * indicate that it is ready for test subject input. Once an input is received,
  * this function will return the time it took for the subject to provide an input.
  *
  * @param reward: Administers reward before illuminating magazine if true,
  * illuminates magazine without administering reward otherwise
  */
unsigned long magOp(bool reward) {
  // Actuates feeder pump, then illuminates and monitors magazine for reward acceptance.
  // Returns reward acceptance latency.
  unsigned long rewardLatency;
  Serial.println("Entered mag op");
  if (reward) {
    Serial.println("Administering reward");
    digitalWrite(FEED_OP, HIGH);
    delay(2000); // TODO: calculate based on pump flow rate, desired reward volume
    digitalWrite(FEED_OP, LOW);
  }
  digitalWrite(MAG_OP, HIGH);
  unsigned long start = millis();
  while (true) {
    if (digitalRead(MAG_REP) == LOW) {
      rewardLatency = millis() - start;
      digitalWrite(MAG_OP, LOW);
      break;
    }
  }
  return rewardLatency;
}

/**
  * @brief Inter-trial period
  *
  * Enforces inter-trial period. When invoked, this function enforces
  * an inter-trial period during which the subject should refrain from touching
  * the touchscreen. The function exits when the subject succeeds in not
  * touching the touchscreen for the period passed in parameter duration.
  * Touching the touchscreen during the inter-trial period resets the time.
  *
  * @param duration: Inter-trial period in milliseconds
  */
void interTrialPeriod(unsigned long duration) {
  bool interTrialPeriodComplete = false;
  unsigned long start;
  while (!interTrialPeriodComplete) {
    tft.touchRead(&tx, &ty);
    start = millis();
    while (true) {
      if (! digitalRead(RA8875_INT)) {
        if (tft.touched()) {
          tft.touchRead(&tx, &ty);
          unsigned long latency = millis() - start;
          break;
        }
      }
      if (millis() - start > duration) {
        interTrialPeriodComplete = true;
        break;
      }
      delay(10);
    }
  }
  tft.touchRead(&tx, &ty);
}

/**
  * @brief TASK - Habituation 1
  *
  * Administers task: Habituation 1
  * A reward is administered, and the magazine is illuminated. 
  *
  * @param duration: Inhibition period in milliseconds
  */
void hab1() {
  unsigned long rewardLatency = magOp(true);
  sprintf(outgoingMsg, "%d", rewardLatency);
  client.publish(topicPub, outgoingMsg);
  interTrialPeriod(4000);
}

/**
  * @brief TASK - Habituation 2
  *
  * Administers task: Habituation 2
  * All 5 choices are illuminated. When the mouse touches any choice,
  * a reward is administered, and the magazine is illuminated. 
  *
  * @param duration: Inhibition period in milliseconds
  */
void hab2() {
  unsigned long touchLatency = 0;
  unsigned long rewardLatency = 0;
  tft.touchRead(&tx, &ty);
  for (int i = 0; i < 5; ++i) {
    illuminateChoice(i);
  }
  unsigned long start = millis();
  while (true) {
    if (! digitalRead(RA8875_INT)) {
      if (tft.touched()) {
        tft.touchRead(&tx, &ty);
        touchLatency = millis() - start;
        extinguishChoices();
        rewardLatency = magOp(true);
        break;
      }
    }
  }
  sprintf(outgoingMsg, "%d %d", touchLatency, rewardLatency);
  client.publish(topicPub, outgoingMsg);
  interTrialPeriod(4000);
}

/**
  * @brief TASK - 5 Choice
  *
  * Administers tasks:
  * 5 CSR CITI
  * 5 CSR VITI
  * RCPT
  * A randomly chosen choice is illuminated for a period specified by parameter
  * stimulusDuration. The subject's response (positive, negative, absent) is noted,
  * and the magazine is operated accordingly. An inter-trial period specified by
  * parameter interTrialDuration is enforced. Parameter variations allow this
  * function to execute 5 CSR CITI, 5 CSR VITI, and RCPT.
  *
  * @param duration: Inhibition period in milliseconds
  */
void fiveChoice(unsigned long stimulusDuration, unsigned long interTrialDuration) {
  unsigned long touchLatency = 0;
  unsigned long rewardLatency = 0;
  int choice = random(0, 5);
  tft.touchRead(&tx, &ty);
  unsigned long start = millis();
  illuminateChoice(choice);
  while (true) {
    if (! digitalRead(RA8875_INT)) {
      if (tft.touched()) {
        tft.touchRead(&tx, &ty);
        touchLatency = millis() - start;
        extinguishChoices();
        if (checkChoiceTouch(tx, ty, choice)) {
          Serial.print("Positive input in ");
          Serial.print(touchLatency);
          Serial.println(" ms");
          rewardLatency = magOp(true);
          break;
        }
        else {
          Serial.print("Negative input in ");
          Serial.print(touchLatency);
          Serial.println(" ms");
          rewardLatency = magOp(false);
          break;
        }
      }
    }
    if (millis() - start > stimulusDuration) {
      extinguishChoices();
      Serial.println("Absent response");
      rewardLatency = magOp(false);
      break;
    }
    delay(10);
  }
  sprintf(outgoingMsg, "%d %d", touchLatency, rewardLatency);
  client.publish(topicPub, outgoingMsg);
  interTrialPeriod(interTrialDuration);
}

/**
  * @brief TASK - Inhibition
  *
  * Administers task: Inhibition.
  * No choices are illuminated. If the subject refrains from touching the screen
  * for the period passed in parameter duration, a reward is administered.
  * If the subject touches the screen during the inhibition period,
  * no reward is administered, and the latency is noted.
  * Trial information is transmitted via MQTT.
  *
  * @param duration: Inhibition period in milliseconds
  */
void inhibitionTrial(unsigned long duration) {
  tft.touchRead(&tx, &ty);
  unsigned long start = millis();
  while (true) {
    if (! digitalRead(RA8875_INT)) {
      if (tft.touched()) {
        tft.touchRead(&tx, &ty);
        unsigned long latency = millis() - start;
        Serial.print("Failed inhibition in ");
        Serial.print(latency);
        Serial.println(" milliseconds");
        magOp(false);
        tft.touchRead(&tx, &ty);
        return;
      }
    }
    if (millis() - start > duration) {
      Serial.println("Inhibition success");
      magOp(true);
      tft.touchRead(&tx, &ty);
      ;
    }
    delay(10);
  }
}

// ------------------------- Setup function -------------------------
void setup() {
  // Serial diagnostic communication begin
  Serial.begin(9600);

  // MQTT topics
  sprintf(topicSub, "%s/stage", subjectID);
  sprintf(topicPub, "%s/data", subjectID);

  // Screen initialization
  if (!tft.begin(RA8875_800x480)) {
    Serial.println("RA8875 Not Found!");
    while (1);
  }
  tft.displayOn(true);
  tft.GPIOX(true); // Enable TFT - display enable tied to GPIOX
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
  client.setServer(mqttServer, 1883);
  client.setCallback(callback);

  // GPIO initialization
  pinMode(FEED_OP, OUTPUT);
  pinMode(MAG_OP, OUTPUT);
  pinMode(MAG_REP, INPUT);
}

// ------------------------- Main loop -------------------------
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  if (millis() - lastCentralComputerPing > 500) {
    lastCentralComputerPing = millis();
    sprintf(outgoingMsg, "ping");
    client.publish(topicPub, outgoingMsg);
  }
}
