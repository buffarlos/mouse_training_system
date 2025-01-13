#include <WiFi.h>
#include <esp_wifi.h>

char mac[17];
char defaultMac[] = "Default MAC Address: ";
char getMacFail[] = "Failed to get MAC Address";

// const char* ssid = ;
// const char* password = ;

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

void setup(){
  Serial.begin(9600);

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

  Serial.print(defaultMac);
  bool macSuccess = getMacAddress();
  if (macSuccess) {
    Serial.println(mac);
  }
  else {
    Serial.println(getMacFail);
  }
}
 
void loop(){

}