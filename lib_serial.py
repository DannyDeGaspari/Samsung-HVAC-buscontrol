#!/usr/bin/python

# Author: Danny De Gaspari

# Library functions for serial access of Samsung HVAC systems

import serial

# define byte position constants
PROTOCOL_START_POS = 0
PROTOCOL_SOURCE_POS = 1
PROTOCOL_DESTINATION_POS = 2
PROTOCOL_COMMAND_POS = 3
PROTOCOL_DATA1_POS = 4
PROTOCOL_DATA2_POS = 5
PROTOCOL_DATA3_POS = 6
PROTOCOL_DATA4_POS = 7
PROTOCOL_DATA5_POS = 8
PROTOCOL_DATA6_POS = 9
PROTOCOL_DATA7_POS = 10
PROTOCOL_DATA8_POS = 11
PROTOCOL_CHECKSUM_POS = 12
PROTOCOL_END_POS = 13

PROTOCOL_START = '\x32'
PROTOCOL_END = '\x34'

def ser_open():
  ser = serial.Serial('/dev/serial0', 2400, serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE, 1)
  return ser
  
def ser_close(ser):
  ser.close()

def print_serline(serline, noprotocol=True):
  if not noprotocol:
    for i in serline:
      print('%2.2X' % i),
  else:
    for i in range(1,12):
      print('%2.2X' % serline[i]),
  print

def ser_capture_msg(ser):
  char = ser.read()
  while char != PROTOCOL_START: # wait for start of message
    char = ser.read()

  serline = []
  serline.append(int(char.encode('hex'),16))
  for x in range(0,13):
    char = ser.read()
    serline.append(int(char.encode('hex'),16))
  return serline

def compose_msg(msg):
  serline = [ord(PROTOCOL_START)]
  chksum = 0
  for x in msg:
    serline.append(x)
    chksum = chksum ^ x   # xor
  serline.append(chksum)
  serline.append(ord(PROTOCOL_END))
  return serline

def ser_transmit_msg(ser, msg):
  # RAW transmit only
  serout = ''
  for x in msg:
    serout = serout + chr(x)
  ser.write(serout)

def ser_send_msg(ser, msg):
  # send message and return response
  wait_idle = True

  # Now wait until the last transmission of a burst of 5 has been transmitted, this is the 0xAD destination.
  # Then there is a 300 ms gap for our own transmission.
  while wait_idle:
    serline = ser_capture_msg(ser)
    if (serline[PROTOCOL_DESTINATION_POS] == 0xAD):
      wait_idle = False

  ser_transmit_msg(ser, msg)
  serline = ser_capture_msg(ser)
  return serline
