#!/usr/bin/python

# Author: Danny De Gaspari

import lib_hvac
import sys, getopt

def set():
  unit = [0,1]
  poweroff = False
  fan = 1
  temp = 20
  mode = 4
  swing = True
  bladepos = 0
  try:
    opts, remainder = getopt.getopt(sys.argv[1:],"hu:of:t:m:s:b:")
  except getopt.GetoptError:
    opts = [('-h', '')]
  for opt, arg in opts:
    if opt == '-h':
      print (sys.argv[0] + '-h -u -o -f -t -m -s')
      print ('options:')
      print ('     -h                : help')
      print ('     -u <unit nbr>     : AC unit number, all units when omitted')
      print ('     -o                : switch AC off')
      print ('     -f <fan speed>    : AUTO, low, med, high')
      print ('     -t <temperature>  : temperature in celsius ('+str(temp)+')')
      print ('     -m <mode>         : auto, cool, dry, fan, HEAT')
      print ('     -s <swing>        : ON, off')
      print ('     -b <blade pos>    : 1-7')
      print ('  example 1: '+ sys.argv[0]+ '-u 0 -t 23 -f auto')
      print ('  example 2: '+ sys.argv[0]+ '-u 0 -o')
      sys.exit()
    elif opt == '-u':
      unit = [int(arg)]
    elif opt == '-o':
      poweroff = True
    elif opt == '-f':
      if arg == 'auto':
        fan = 0
      elif arg == 'low':
        fan = 2
      elif arg == 'med':
        fan = 4
      elif arg == 'high':
        fan = 5
    elif opt == '-t':
      temp = int(arg)
    elif opt == '-m':
      if arg == 'auto':
        mode = 0
      elif arg == 'cool':
        mode = 1
      elif arg == 'dry':
        mode = 2
      elif arg == 'fan':
        mode = 3
      elif arg == 'heat':
        mode = 4
    elif opt == '-s':
      if arg == 'on':
        swing = True
      else:
        swing = False
    elif opt == '-b':
      bladepos = int(arg)
      if bladepos < 1:
        bladepos = 1
      elif bladepos > 7:
        bladepos = 7

  ser = lib_hvac.ser_open()
  if ser == -1:
    print ('Error opening serial port.')
    return -1

  for i in unit:
    msg = []
    msg.append(0x85 )
    msg.append(0x20 + i )
    msg.append(0xa0 )
    if swing:
      msg.append(0x1a )
    else:
      msg.append(0x1f )
    msg.append(0x18 )
    msg.append((fan << 5) + temp)
    msg.append(mode)
    if poweroff:
      msg.append(0xc4 )
    else:
      msg.append(0xf4 )
    msg.append(0x0  )
    if bladepos > 0:
      msg.append(0x10 + bladepos)
    else:
      msg.append(0x0  )
    msg.append(0x0  )

    sermsg = lib_hvac.compose_hvac_msg(msg)
    serline = lib_hvac.ser_send_hvac_msg(ser, sermsg)
    lib_hvac.print_serline(serline)

  print('The end.')
  lib_hvac.ser_close(ser)

if __name__== "__main__":
  set()