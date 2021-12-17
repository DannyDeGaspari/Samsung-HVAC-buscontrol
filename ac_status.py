#!/usr/bin/python3

# Author: Danny De Gaspari

import lib_hvac

AC_Fan = ['auto', 'off', 'low', '', 'med', 'high']
AC_Mode = ['auto', 'cool', 'dry', 'fan', 'heat']

class AC_Unit():
  address = 0
  on_off = 0
  settemp = 0
  usedtemp = 0
  roomtemp = 0
  roomtempacc = 0
  fan = 0
  swing = 0
  mode = 0

  def __init__(self, address):
      self.address = address

def get_status(units):

  ser = lib_hvac.ser_open()
  if ser == -1:
    return -1


  for unit in units:
    cmd_52 = False
    cmd_53 = False
    cmd_64 = False
    collect_info = True
    
    while collect_info:
      serline = lib_hvac.ser_capture_hvac_msg(ser)
      if (serline[lib_hvac.PROTOCOL_SOURCE_POS] == unit.address):
        if (serline[lib_hvac.PROTOCOL_COMMAND_POS] == 0x52):
          cmd_52 = True
          unit.settemp = (serline[lib_hvac.PROTOCOL_DATA1_POS] & 0x3f) + 9
          unit.roomtemp = (serline[lib_hvac.PROTOCOL_DATA2_POS] & 0x3f) + 9
          unit.fan = (serline[lib_hvac.PROTOCOL_DATA4_POS] & 0x07)
          unit.swing = (serline[lib_hvac.PROTOCOL_DATA4_POS] & 0xf8) != 0xF8
          unit.on_off = (serline[lib_hvac.PROTOCOL_DATA5_POS] & 0x80) == 0x80
        if (serline[lib_hvac.PROTOCOL_COMMAND_POS] == 0x53):
          cmd_53 = True
          unit.mode = (serline[lib_hvac.PROTOCOL_DATA8_POS] & 0x07)
        if (serline[lib_hvac.PROTOCOL_COMMAND_POS] == 0x64):
          cmd_64 = True
          unit.usedtemp = (serline[lib_hvac.PROTOCOL_DATA3_POS] * 256 + serline[lib_hvac.PROTOCOL_DATA4_POS] - 553) / 10.0
          unit.roomtempacc = (serline[lib_hvac.PROTOCOL_DATA5_POS] * 256 + serline[lib_hvac.PROTOCOL_DATA6_POS] - 553) / 10.0
      collect_info = not(cmd_52 and cmd_53 and cmd_64)
  
  lib_hvac.ser_close(ser)
  return 0

if __name__== "__main__":
  units = [AC_Unit(0x20), AC_Unit(0x21)]

  print ('Reading status...')
  if get_status(units) != -1:
    for unit in units:
      print ('\nUnit: 0x%x' % unit.address)
      print ('Power         :', unit.on_off)
      print ('Set temp      :', unit.settemp)
      print ('Room temp     :', unit.roomtemp)
      print ('Used temp     :', unit.usedtemp)
      print ('Acc Room temp :', unit.roomtempacc)
      if unit.on_off:
        print ('Fan           :', AC_Fan[unit.fan])
        print ('Swing         :', unit.swing)
        print ('Mode          :', AC_Mode[unit.mode])
  else:
    print ('Status get failed')
