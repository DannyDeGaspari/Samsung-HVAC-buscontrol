# Samsung-HVAC-buscontrol
## Purpose
Samsung airconditioners can be controlled by a wired remote controller. I was wondering if I could replace the wired remote controller with my own home automation system. Thats why I started to investigate how the communication works between the controller and the airconditioner.
So far I reverse engineered the communication protocol and with the information I found I can already do some basic control of the airconditioning. The purpose of this repository is to complete the protocol details as much as possible to allow anybody else connect Samsung airconditioners to their own home automation systems.

Note that this does not describe the communication protocol of a wireless IR controller !!

## Physical layer
The physical layer is a 2 wire RS-485 communications bus. Each unit has 2 such busses. The wires are labelled F1, F2, F3 and F4. F1 and F2 are used for communications with the outdoor unit, the F3 and F4 wires are used for the wired remote control.

## Protocol
Serial communication settings used on the bus are 2400 baud, 8E1. The wired remote control is the master, the indoor units are the slaves. The wired remote control send commands as a message of 14 bytes. The units respond with a similar message with the same length.
The protocol can be described as follows:

<start> <src> <dst> <cmd> <data: 8 bytes> <chksum> <end>

With:
Byte   Identifier   Comments
----------------------------
1      Start  : start of message (0x32)
2      Src    : Source address
3      Dst    : Destination address
4      Cmd    : Command byte
5-12   Data   : Data is always 8 bytes in length, unused bytes will be zero
13     Chksum : Checksum of message which is the XOR of bytes 2-12
14     End    : end of message (0x34)
