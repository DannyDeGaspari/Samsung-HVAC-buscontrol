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

PROTOCOL_START = b'\x32'
PROTOCOL_END = b'\x34'
PROTOCOL_LENGTH = 14

def ser_open(port='/dev/serial0'):
  try:
    ser = serial.Serial(port, 2400, serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE, 1, exclusive=True)
  except:
    return -1
  else:
    return ser

def ser_close(ser):
  ser.close()

def print_heading(noprotocol=True):
  if not noprotocol:
    print('STA SRC DST CMD DATA                            CHK END')
    print('-------------------------------------------------------')
  if noprotocol:
    print('SRC DST CMD DATA                            ')
    print('--------------------------------------------')

def print_serline(serline, noprotocol=True):
  if not noprotocol:
    for i in serline:
      #print('%2.2X' % ord(i), end = ' '),
      print('%2.2X' % i, end = '  ' )
  else:
    for i in range(1,12):
      #print('%2.2X' % ord(serline[i]), end = ' '),
      print('%2.2X' % serline[i], end = ' ')
  print()

def ser_capture_hvac_msg(ser):
  msg = ser.read_until(PROTOCOL_START,30) # read until start of new message
  msg = ser.read(PROTOCOL_LENGTH - 1) # read remaining message
  msg = PROTOCOL_START + msg 
  return msg

def compose_hvac_msg(msg):
  serline = bytearray()
  serline.append(ord(PROTOCOL_START))
  chksum = 0
  for x in msg:
    serline.append(x)
    chksum = chksum ^ x   # xor
  serline.append(chksum)
  serline.append(ord(PROTOCOL_END))
  #print('composed :', serline)
  return serline

def ser_send_hvac_msg(ser, msg):
  # send message and return response
  wait_idle = True
  #print_heading(False)

  # Now wait until the last transmission of a burst of 5 has been transmitted, this is the 0xAD destination.
  # Then there is a 300 ms gap for our own transmission.
  while wait_idle:
    serline = ser_capture_hvac_msg(ser)
    #print_serline(serline,False)
    if (serline[PROTOCOL_DESTINATION_POS] == 0xAD):
      wait_idle = False

  ser.write(msg)
  serline = ser_capture_hvac_msg(ser)
  return serline
