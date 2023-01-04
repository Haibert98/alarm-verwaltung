#include <WiFi.h>
#include "time.h"
extern "C"
{
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"
}
#include <AsyncMqttClient.h>
#include <Adafruit_NeoPixel.h>

#define BUTTON_PIN 21
#define LED_PIN 22
// 1 wenn im livingplace, 0 wenn zu Hause
#define LivingPlace 0

#if LivingPlace==1
#define WIFI_SSID "LP HotSpot"
#define WIFI_PASSWORD "LP HotSpot"
//Haidars Broker
#define MQTT_HOSTNAME "dashboard.lp.smsy.haw-hamburg.de"//"broker.hivemq.com"//
#define MQTT_PORT 1901//1883
#else
#define WIFI_SSID "NETGEAR55"
#define WIFI_PASSWORD "modernroad80"
#define MQTT_HOSTNAME "broker.hivemq.com"
#define MQTT_PORT 1883
#endif

//0 wenn ESP keine Internetverbindung aufbauen soll, 1 sonst
#define INTERNET 1

int lastState = HIGH;
int currentState;
int64_t oldTS;


AsyncMqttClient mqttClient;
TimerHandle_t mqttReconnectTimer;
TimerHandle_t wifiReconnectTimer;
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(1, LED_PIN, NEO_GRB + NEO_KHZ800);

void connectToWifi(){
  WiFi.disconnect();
  Serial.println("Disconnected");
  WiFi.mode(WIFI_STA);
  Serial.println("Beginning");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED){
    Serial.printf("WiFi.status: %i\n",WiFi.status());
    delay(1000);
  }
  Serial.println("WiFi connected");
}

void connectToMqtt(){
  Serial.println("Connecting to MQTT...");
  mqttClient.connect();
}

void WiFiEvent(WiFiEvent_t event){
  Serial.printf("[WiFi-event] event: %d\n", event);
  switch (event)
  {
  case SYSTEM_EVENT_STA_GOT_IP:
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    connectToMqtt();
    break;
  case SYSTEM_EVENT_STA_DISCONNECTED:
    Serial.println("WiFi lost connection");
    xTimerStop(mqttReconnectTimer, 0); // ensure we don't reconnect to MQTT while reconnecting to Wi-Fi
    xTimerStart(wifiReconnectTimer, 0);
    break;
  }
}

void onMqttConnect(bool sessionPresent){
  Serial.println("Connected to MQTT");
}

void onMqttDisconnect(AsyncMqttClientDisconnectReason reason){
  Serial.println("Disconnected from MQTT");
  if (WiFi.isConnected()){
    xTimerStart(mqttReconnectTimer, 0);
  }
}

void onMqttSubscribe(uint16_t packetId, uint8_t qos){
  Serial.println("Subscribe acknowledged");
}

void onMqttUnsubscribe(uint16_t packetId){
  Serial.println("Unsubscribe acknowledged");
}

void onMqttMessage(char *topic, char *payload, AsyncMqttClientMessageProperties properties, size_t len, size_t index, size_t total){
  Serial.println("Message received");
  Serial.print("  topic: ");
  Serial.println(topic);
  Serial.print("  payload: ");
  Serial.println(payload);

  if(strcmp(topic,"signal/klingel/led")==0){
    std::string str(payload);
    if(str.rfind("clear")!= std::string::npos){
      pixels.clear();
      pixels.show();
    }else{
      if(str.rfind("gruen")!= std::string::npos){
        pixels.setPixelColor(0, pixels.Color(0, 255, 0)); 
        pixels.show();
      }else if(str.rfind("rot")!= std::string::npos){
        pixels.setPixelColor(0, pixels.Color(255, 0, 0)); 
        pixels.show();
       }else if(str.rfind("orange")!= std::string::npos){
        pixels.setPixelColor(0, pixels.Color(255, 165, 0)); 
        pixels.show();
      }else{
        Serial.println("  Didnt change, wasnt gruen or rot");
      }
    }
  }
}

void onMqttPublish(uint16_t packetId){ 
}

void setup(){
  Serial.begin(9600);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pixels.begin();
  pixels.clear();
  pixels.show();
  Serial.println();
  Serial.println();

  #if INTERNET == 1
  mqttReconnectTimer = xTimerCreate("mqttTimer", pdMS_TO_TICKS(2000), pdFALSE, (void *)0, reinterpret_cast<TimerCallbackFunction_t>(connectToMqtt));
  wifiReconnectTimer = xTimerCreate("wifiTimer", pdMS_TO_TICKS(2000), pdFALSE, (void *)0, reinterpret_cast<TimerCallbackFunction_t>(connectToWifi));

  //WiFi.onEvent(WiFiEvent); //macht Probleme

  mqttClient.onConnect(onMqttConnect);
  mqttClient.onDisconnect(onMqttDisconnect);
  mqttClient.onSubscribe(onMqttSubscribe);
  mqttClient.onUnsubscribe(onMqttUnsubscribe);
  mqttClient.onMessage(onMqttMessage);
  mqttClient.onPublish(onMqttPublish);
  mqttClient.setServer(MQTT_HOSTNAME, MQTT_PORT);
  
  connectToWifi();
  connectToMqtt();
  delay(1000);
  mqttClient.subscribe("signal/klingel/led",2);
  #endif
}

int buttonPresses = 0;
void loop(){
  // read the state of the switch/button:
  currentState = digitalRead(BUTTON_PIN);

  if ((lastState == LOW && currentState == HIGH) || (lastState == HIGH && currentState == LOW)){
    if (buttonPresses==0){
      struct timeval tv_now;
      gettimeofday(&tv_now, NULL);
      oldTS = (int64_t)tv_now.tv_sec * 1000000L + (int64_t)tv_now.tv_usec;
      buttonPresses++;
    }else{
      struct timeval tv_now;
      gettimeofday(&tv_now, NULL);
      int64_t newTS = (int64_t)tv_now.tv_sec * 1000000L + (int64_t)tv_now.tv_usec;
      int tsDifference = newTS - oldTS;
      oldTS = newTS;

      if(lastState == LOW && currentState == HIGH){
        char int_str[20];
        sprintf(int_str, "%d", tsDifference);
        #if INTERNET == 1
        mqttClient.publish("signal/klingel", 2, false, (int_str));
        #else
        Serial.printf("tsDifference: \n", tsDifference);
        #endif
      }
      
    }
  }
  // save the last state
  lastState = currentState;
  delay(2);
}