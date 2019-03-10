#!/usr/bin/python

# Author: Danny De Gaspari

import serial
import sys, getopt

def print_serline(serline, noprotocol):
  if not noprotocol:
    for i in serline:
      print('%2.2X' % i),
  else:
    for i in range(1,12):
      print('%2.2X' % serline[i]),
  print

# filters:
src = -1
dst = -1
cmd = []
nbr = 25
full = False
forever = False
opts, args = getopt.getopt(sys.argv[1:],"hs:d:c:n:f")
for opt, arg in opts:
  if opt == '-h':
    print sys.argv[0], '-h -s -d -c -n'
    print 'options:'
    print '     -h                : help'
    print '     -s <source>       : source filter'
    print '     -d <destination>  : destination filter'
    print '     -c <command>      : command filter, more commands possible'
    print '     -n <number>       : number of messages to dump, 0 for infinite'
    print '     -f                : display full message'
    print '  values for filters will be interpreted as hex'
    print '  protocol: <start (32)> <src> <dst> <cmd> <data: 8 bytes> <chksum> <end (34)>'
    print '  example 1: ', sys.argv[0], '-s 0x80 -c 0x52'
    print '  example 2: ', sys.argv[0], '-c a0 -c 50 -n 0'
    sys.exit()
  elif opt == '-s':
    src = int(arg,16)
  elif opt == '-d':
    dst = int(arg,16)
  elif opt == '-c':
    cmd.append( int(arg,16) )
  elif opt == '-n':
    nbr = int(arg)
    if nbr == 0:
      forever = True
  elif opt == '-f':
    full = True
         
ser = serial.Serial('/dev/serial0', 2400, serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE, 1)
print 'Capturing on:', ser.name
char = ser.read()
while nbr > 0 or forever:
  while char != '\x32': # wait for start of message
    char = ser.read()

  serline = []
  for x in range(0,14):
    #print('%2.2X' % int(char.encode('hex'),16)),
    serline.append(int(char.encode('hex'),16))
    char = ser.read()
  if (serline[1] == src or src == -1) and (serline[2] == dst or dst == -1) and (serline[3] in cmd or not cmd):
    print_serline(serline, not full)
    nbr=nbr-1

print('The end.')
ser.close()
