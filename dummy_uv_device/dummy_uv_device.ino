/* 
 * File:   dummy_uv_device.ino
 * Author: Jan Molina
 * 
 * Description:
 * 
 *   Small program that mimics the behavior of the real UV device.
 *   This can run on any AVR board, but the pin numbers in this code assume
 *   an Arduino NANO is used.
 *   
 * Device:
 *
 *   Arduino NANO
 * 
 * Created on December 30, 2024, 8:52 AM
 */
 
const int PIN_UV_LED = 2;



void setup()
{
  pinMode(PIN_UV_LED, OUTPUT);
  
  // Simple startup sequence
  digitalWrite(PIN_UV_LED, HIGH);
  delay(5000);
  digitalWrite(PIN_UV_LED, LOW);
}

void loop()
{
  
}
