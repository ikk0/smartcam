// Smart Camera, Alexa controlled face recognition door bell
// 
// This demo can only work on OV2640_MINI_2MP platform.
//
// When switch is pressed, the camera caputures a JPG image.
// The JPG data is read from the SPI bus in chunks and directly sent out using http put request 
// in order to avoid the need of storing it into ram or on SD Card.
//
// (C) 2018 Sebastian Enzinger & Markus Enzinger

#include <Wire.h>          // library for Arduino ports
#include <ArduCAM.h>       // library for Arducam
#include <SPI.h>           // library for SPI communications
#include "memorysaver.h"   // configures the camera type used
#include <Ethernet.h>      // library for ethernet shield
#define switch 5 // GPIO pin for the door bell switch
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xF1, 0xED };    // Ethernet Mac Address to use for the ethernet shield
char host[] = "d35xafoveji7v.cloudfront.net";           // Where to send the image by http post request

const int CS = 7;         // set pin 7 as the slave select for the cam module's spi port:
bool is_header = false;
int mode = 0;
uint8_t start_capture = 0;
ArduCAM myCAM( OV2640, CS );
uint8_t read_fifo_burst(ArduCAM myCAM);
EthernetClient client;
//-------------------------------------------------------------------  setup() section -----------------------
void setup() {
// put your setup code here, to run once:
uint8_t vid, pid;
uint8_t temp;
IPAddress dnServer(192, 168, 3, 5);     // the dns server ip
IPAddress gateway(192, 168, 3, 5);      // the router's gateway address
IPAddress subnet(255, 255, 255, 0);     // the subnet
IPAddress ip(192, 168, 3, 251);         //the IP address of our ethernet shield
Ethernet.begin(mac, ip, dnServer, gateway, subnet);       // Initialize Ethernet Shield
Wire.begin();
Serial.begin(115200);                                     // Initialize Serial Output for debug messages
Serial.println(F("ArduCAM Start!"));
// set the CS as an output:
pinMode(CS, OUTPUT);                    // Chip select line to arducam
pinMode(switch, INPUT_PULLUP);          // Switch input: set pullup to read "high" when not pressed
// initialize SPI:
SPI.begin();
while(1){
  //Check if the ArduCAM SPI bus is OK
  myCAM.write_reg(ARDUCHIP_TEST1, 0x55);
  temp = myCAM.read_reg(ARDUCHIP_TEST1);
  if (temp != 0x55){
    Serial.println(F("ACK CMD SPI interface Error!"));
    delay(1000);continue;
  }else{
    Serial.println(F("ACK CMD SPI interface OK."));break;
  }
}
while(1){                           //Check if the camera module type is OV2640
    myCAM.wrSensorReg8_8(0xff, 0x01);
    myCAM.rdSensorReg8_8(OV2640_CHIPID_HIGH, &vid);
    myCAM.rdSensorReg8_8(OV2640_CHIPID_LOW, &pid);
    if ((vid != 0x26 ) && (( pid != 0x41 ) || ( pid != 0x42 ))){
      Serial.println(F("ACK CMD Can't find OV2640 module!"));
      delay(1000);continue;
    }
    else{
      Serial.println(F("ACK CMD OV2640 detected."));break;
    } 
}
myCAM.set_format(JPEG);          //Change to JPEG capture mode and initialize the OV2460 module
myCAM.InitCAM();
delay(1000);
myCAM.clear_fifo_flag();
}

//------------------------------------------------------------------ LOOP section ---------------------
void loop() {
uint8_t temp = 0xff, temp_last = 0;
uint32_t len;
bool is_header = false, errorflag=false;
int inChar;
if (digitalRead(switch))   // Switch pressed?
{
    myCAM.OV2640_set_JPEG_size(OV2640_800x600);  // set image resolution in Arducam module
    delay(1000);   
    Serial.println(F("ACK CMD switch to OV2640_800x600"));
    temp = 0xff;
    myCAM.flush_fifo();
    myCAM.clear_fifo_flag();
    myCAM.start_capture();                                   // start image capture
    start_capture = 0;
    while (!myCAM.get_bit(ARDUCHIP_TRIG, CAP_DONE_MASK));    // check if capture is finished
    len = myCAM.read_fifo_length();
    Serial.println(len);
    if ((len >= MAX_FIFO_SIZE) | (len == 0))                 // check for invalid image size
      {
        myCAM.clear_fifo_flag();
        Serial.println(F("ERR wrong size"));
        errorflag=1;
      }
    Serial.println(F("ACK CMD CAM Capture Done."));
    if (!client.connect(host, 80)) {                         // connect to host
        Serial.println("ERR http connection failed");
        errorflag=1;
    }
    if (!errorflag) {
      myCAM.CS_LOW();                                        // switch CS line of camera active
      myCAM.set_fifo_burst();//Set fifo burst mode
      SPI.transfer(0xFF);
      myCAM.CS_HIGH();                                       // switch CS line of camera inactive to allow ethernet shield to use SPI bus
      String response = "POST /prod/smartcamIdentifyPerson HTTP/1.1\r\n";
      response += "Host: d35xafoveji7v.cloudfront.net\r\n";
      response += "Content-Type: image/jpeg\r\n";
      response += "Content-Length: " + String(len) + "\r\n";
      Serial.println("connected to the server");
      client.println(response); 
      static const size_t bufferSize = 512;
      static uint8_t buffer[bufferSize] = {0xFF};
      while (len) {                                         // read chunks of 512 byte and send them out to host, because of memory constraints
        size_t will_copy = (len < bufferSize) ? len : bufferSize;
        myCAM.CS_LOW();
        myCAM.set_fifo_burst();//Set fifo burst mode
        for (int bufptr=0; bufptr<will_copy; bufptr++) 
          buffer[bufptr]=SPI.transfer(0x00); 
        myCAM.CS_HIGH();
        if (client.connected()) 
          client.write(&buffer[0], will_copy);
        len -= will_copy;
      }   
    } 
    myCAM.CS_HIGH();
    int connectLoop=0;
    while(client.connected())                               // Sending complete, now read response from host and forward to serial monitor
     {
       while(client.available())
        {
          inChar = client.read();
          Serial.write(inChar);
          connectLoop = 0;                             // set connectLoop to zero if a packet arrives
        }
       connectLoop++;
       if(connectLoop > 2000)                         // if more than 1000 milliseconds since the last packet
       {
         Serial.println();
         client.stop();                                // then close the connection from this end.
       }
       delay(1);
     }
  }
}
