/**
  * Automated Training System Firmware
  * To be compiled by Arduino IDE and flashed onto training system ESP32
  * NOTE: Uncomment and fill network params before flashing firmware!
  */

// ------------------------- Imports -------------------------
#include "Adafruit_GFX.h"
#include "Adafruit_RA8875.h"
#include <WiFi.h>
#include <esp_wifi.h>
#include <PubSubClient.h>
#include <math.h>

// ------------------------- Pin name definitions -------------------------
// Touchscreen library only supports hardware SPI at this time
// Connect SCLK to ESP32-PROS3 Digital #36 (Hardware SPI clock)
// Connect MISO to ESP32-PROS3 Digital #37 (Hardware SPI MISO)
// Connect MOSI to ESP32-PROS3 Digital #35 (Hardware SPI MOSI)
#define RA8875_INT 9
#define RA8875_CS 34
#define RA8875_RESET 39
#define FEED_OP 12
#define MAG_OP 13
#define MAG_REP 42

// ------------------------- Constants -------------------------
// Conversions
const int msPerSecond = 1000;
/*
########################################################
### 5 Choice parameters - fill with info, then flash ###
########################################################
*/
// 5 choice location and size information
const int choiceXPos[5] = {26, 188, 350, 512, 674};
const int choiceYPos = 365;
const int choiceSize = 100;
/*
######################################################
### Feeder parameters - fill with info, then flash ###
######################################################
*/
const float pumpFlowRate = 0.025; // milliliters per second
const float rewardVolume = 0.01; // milliliters
const unsigned long feedOpTime =
  round((rewardVolume/pumpFlowRate)*msPerSecond); // milliseconds
/*
#######################################################
### Network parameters - fill with info, then flash ###
#######################################################
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
char topicReq[30];
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
  if (x/xScale > (choiceXPos[choice])
    && x/xScale < (choiceXPos[choice] + choiceSize)
    && y/yScale > choiceYPos && y/yScale < (choiceYPos + choiceSize)) {
    return true;
  }
  return false;
}

/**
  * @brief Extinguishes all 5 choices
  *
  * This function extinguishes all 5 choices on the touchscreen by drawing over
  * them with black squares.
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

// MQTT helpers
/**
  * @brief Attempts to connect to MQTT network if not connected
  *
  * This function will attempt to connect to the MQTT network if currently
  * disconnected.
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
  * This function is invoked when an MQTT message arrives on the subscribed
  * topic. In turn, this function invokes the appropriate training function
  * based on the message contents.
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
    else if (messageTemp == "rcpt_viti_2_to_1") {
      unsigned long interTrialDuration = random(2, 7);
      interTrialDuration = interTrialDuration*1000;
      fiveChoice(2000, interTrialDuration);
    }
    else if (messageTemp == "rcpt_viti_2") {
      unsigned long interTrialDuration = random(2, 7);
      interTrialDuration = interTrialDuration*1000;
      fiveChoice(2000, interTrialDuration);
    }
    else if (messageTemp == "rcpt_viti_175") {
      unsigned long interTrialDuration = random(2, 7);
      interTrialDuration = interTrialDuration*1000;
      fiveChoice(1750, interTrialDuration);
    }
    else if (messageTemp == "rcpt_viti_15") {
      unsigned long interTrialDuration = random(2, 7);
      interTrialDuration = interTrialDuration*1000;
      fiveChoice(1500, interTrialDuration);
    }
  }
}

// ------------------------- Training functions -------------------------
/**
  * @brief Operates the feeder magazine
  *
  * When invoked, this function administers a food reward if parameter reward is
  * true. Then, it will illuminate the magazine to indicate that it is ready for
  * test subject input. Once an input is received, this function will return the
  * time it took for the subject to provide an input.
  *
  * @param reward: Administers reward before illuminating magazine if true,
  * illuminates magazine without administering reward otherwise
  */
unsigned long magOp(bool reward) {
  unsigned long rewardLatency;
  Serial.println("Entered mag op");
  if (reward) {
    Serial.println("Administering reward");
    digitalWrite(FEED_OP, HIGH);
    delay(feedOpTime);
    digitalWrite(FEED_OP, LOW);
  }
  digitalWrite(MAG_OP, HIGH);
  Serial.println("Magazine illuminated");
  unsigned long start = millis();
  while (true) {
    if (digitalRead(MAG_REP) == LOW) {
      rewardLatency = millis() - start;
      Serial.print("Magazine input in ");
      Serial.print(rewardLatency);
      Serial.println(" ms");
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
  * A reward is administered, and the magazine is illuminated. Task data is
  * reported via MQTT. An inter-trial period of 4 seconds is enforced.
  */
void hab1() {
  int positive = 0;
  int negative = 0;
  int premature = 0;
  int omission = 0;
  int positiveWithhold = 0;
  int negativeWithhold = 0;
  unsigned long correctLatency = 0;
  unsigned long incorrectLatency = 0;
  unsigned long rewardLatency = 0;
  unsigned long prematureLatency = 0;

  rewardLatency = magOp(true);
  sprintf(outgoingMsg, "0 0 0 0 0 0 0 0 %d 0 0", rewardLatency);
  if (!client.connected()) {
    reconnect();
  }
  client.publish(topicPub, outgoingMsg);
  interTrialPeriod(4000);
}

/**
  * @brief TASK - Habituation 2
  *
  * Administers task: Habituation 2
  * All 5 choices are illuminated. When the mouse touches any choice,
  * a reward is administered, and the magazine is illuminated. Task data is
  * reported via MQTT. An inter-trial period of 4 seconds is enforced.
  */
void hab2() {
  int positive = 0;
  int negative = 0;
  int premature = 0;
  int omission = 0;
  int positiveWithhold = 0;
  int negativeWithhold = 0;
  unsigned long correctLatency = 0;
  unsigned long incorrectLatency = 0;
  unsigned long rewardLatency = 0;
  unsigned long prematureLatency = 0;

  tft.touchRead(&tx, &ty);
  for (int i = 0; i < 5; ++i) {
    illuminateChoice(i);
  }
  unsigned long start = millis();
  while (true) {
    if (! digitalRead(RA8875_INT)) {
      if (tft.touched()) {
        tft.touchRead(&tx, &ty);
        positive = 1;
        correctLatency = millis() - start;
        extinguishChoices();
        rewardLatency = magOp(true);
        break;
      }
    }
  }
  sprintf(outgoingMsg, "%d 0 0 0 0 0 %d 0 %d 0 0", positive, correctLatency, rewardLatency);
  if (!client.connected()) {
    reconnect();
  }
  client.publish(topicPub, outgoingMsg);
  interTrialPeriod(4000);
}

/**
  * @brief TASK - 5 Choice
  *
  * Administers tasks: 5 CSR CITI, 5 CSR VITI, RCPT
  * A randomly chosen choice is illuminated for a period specified by parameter
  * stimulusDuration. If the subject touches the illuminated choice within the
  * time period defined by parameter stimulusDuration, a reward is administered,
  * and the magazine is illuminated. If the subject touches an incorrect choice
  * or fails to provide an input within the time period defined by parameter
  * stimulusDuration, no reward is administered, and the magazine is
  * illuminated. Task data is reported via MQTT. An inter-trial period defined
  * by parameter interTrialDuration is enforced.
  *
  * @param stimulusDuration: Stimulus period in milliseconds
  * @param interTrialDuration: Inter-trial period in milliseconds
  */
void fiveChoice(unsigned long stimulusDuration,
  unsigned long interTrialDuration) {
  int positive = 0;
  int negative = 0;
  int premature = 0;
  int omission = 0;
  int positiveWithhold = 0;
  int negativeWithhold = 0;
  unsigned long correctLatency = 0;
  unsigned long incorrectLatency = 0;
  unsigned long rewardLatency = 0;
  unsigned long prematureLatency = 0;

  int choice = random(0, 5);
  tft.touchRead(&tx, &ty);
  unsigned long start = millis();
  illuminateChoice(choice);
  while (true) {
    if (! digitalRead(RA8875_INT)) {
      if (tft.touched()) {
        tft.touchRead(&tx, &ty);
        extinguishChoices();
        if (checkChoiceTouch(tx, ty, choice)) {
          correctLatency = millis() - start;
          Serial.print("Positive input in ");
          Serial.print(correctLatency);
          Serial.println(" ms");
          positive = 1;
          rewardLatency = magOp(true);
          break;
        }
        else {
          incorrectLatency = millis() - start;
          Serial.print("Negative input in ");
          Serial.print(incorrectLatency);
          Serial.println(" ms");
          negative = 1;
          rewardLatency = magOp(false);
          break;
        }
      }
    }
    if (millis() - start > stimulusDuration) {
      extinguishChoices();
      Serial.println("Absent response");
      omission = 1;
      rewardLatency = magOp(false);
      break;
    }
    delay(10);
  }
  sprintf(outgoingMsg, "%d %d 0 %d 0 0 %d %d %d 0 %d", positive, negative, omission, correctLatency, incorrectLatency, rewardLatency, interTrialDuration);
  if (!client.connected()) {
    reconnect();
  }
  client.publish(topicPub, outgoingMsg);
  interTrialPeriod(interTrialDuration);
}

/**
  * @brief TASK - Inhibition
  *
  * Administers task: Inhibition.
  * No choices are illuminated. If the subject refrains from touching the screen
  * for the period passed in parameter duration, a reward is administered, and
  * the magazine is illuminated. If the subject touches the screen during the
  * inhibition period, no reward is administered, and the magazine is
  * illuminated. Trial information is transmitted via MQTT.
  *
  * @param duration: Inhibition period in milliseconds
  */
void inhibitionTrial(unsigned long duration) {
  int positive = 0;
  int negative = 0;
  int premature = 0;
  int omission = 0;
  int positiveWithhold = 0;
  int negativeWithhold = 0;
  unsigned long correctLatency = 0;
  unsigned long incorrectLatency = 0;
  unsigned long rewardLatency = 0;
  unsigned long prematureLatency = 0;

  tft.touchRead(&tx, &ty);
  unsigned long start = millis();
  while (true) {
    if (! digitalRead(RA8875_INT)) {
      if (tft.touched()) {
        tft.touchRead(&tx, &ty);
        negativeWithhold = 1;
        prematureLatency = millis() - start;
        Serial.print("Failed inhibition in ");
        Serial.print(prematureLatency);
        Serial.println(" milliseconds");
        rewardLatency = magOp(false);
        tft.touchRead(&tx, &ty);
        break;
      }
    }
    if (millis() - start > duration) {
      positiveWithhold = 1;
      Serial.println("Inhibition success");
      rewardLatency = magOp(true);
      tft.touchRead(&tx, &ty);
      break;
    }
    delay(10);
  }
  sprintf(outgoingMsg, "0 0 0 0 %d %d 0 0 %d %d 0", positiveWithhold, negativeWithhold, prematureLatency, rewardLatency);
  if (!client.connected()) {
    reconnect();
  }
  client.publish(topicPub, outgoingMsg);
  interTrialPeriod(4000);
}

// ------------------------- Setup function -------------------------
void setup() {
  // Serial diagnostic communication begin
  Serial.begin(9600);

  // MQTT topics
  sprintf(topicSub, "%s/stage", subjectID);
  sprintf(topicPub, "%s/data", subjectID);
  sprintf(topicReq, "%s/request", subjectID);

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
  // If disconnected from MQTT, reconnect before proceeding.
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  // If more than 500 milliseconds since last ping, ping central computer.
  if (millis() - lastCentralComputerPing > 500) {
    lastCentralComputerPing = millis();
    sprintf(outgoingMsg, "ping");
    client.publish(topicReq, outgoingMsg);
  }
}
