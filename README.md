# Samsung-HVAC-buscontrol
## Purpose
Samsung airconditioners can be controlled by a wired remote controller (MWR-WE10). I was wondering if I could replace the wired remote controller with my own home automation system. Thats why I started to investigate how the communication works between the controller and the airconditioner.
So far I reverse engineered the communication protocol and with the information I found I can already do some basic control of the airconditioning. The purpose of this repository is to complete the protocol details as much as possible to allow anybody else connect Samsung airconditioners to their own home automation systems.

Note that this does not describe the communication protocol of a wireless IR controller !!

## Physical layer
The physical layer is a 2 wire RS-485 communications bus. Each unit has 2 such busses. The wires are labelled F1, F2, F3 and F4. F1 and F2 are used for communications with the outdoor unit, the F3 and F4 wires are used for the wired remote control.

## Protocol
Serial communication settings used on the bus are 2400 baud, 8E1. The wired remote control is the master, the indoor units are the slaves. The wired remote control send commands as a message of 14 bytes. The units respond with a similar message with the same length.
The protocol can be described as follows:

```
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
```

In my case the address of the wired remote control is 0x84, the address of my 2 indoor units are 0x20 and 0x21.
The master sends a command to a slave, the slave responds to the master.
An example communication can look like this (all values are hex and xx represent any value):

```
Command:
32 84 20 53 xx xx xx xx xx xx xx xx xx 34
Reply:
32 20 84 53 xx xx xx xx xx xx xx xx xx 34
```

That was the easy part of the communication sniffing. The difficult part is to find out the meaning of all commands and the meaning of al bytes for each command/response.

## Command table
I made an Excel sheet with all commands that I saw passing on the comms and also tried to fill in all information that the data bytes contains. So the list is still incomplete.

| Cmd | Description |
| :---: | :--- |
| A0  | Change settings command |
|     | Unit replies with 50 |

| Data byte | Settings |
| :---: | :--- |
| 1 | <p>bit 4-0 : 0x1a = blade swing up/down<br>0x1f = blade swing off</p> |
|   | bit 5 : sleep |
| 2 | 0 |
| 3 | bit 4-0 : temperature setting |
|   | <p>bit 7-5 : fan speed<br>0 = auto<br>2 = low<br>4 = medium<br>5 = high</p> |
| 4 | <p>bit 2-0 : mode<br>0 = auto<br>1 = cool<br>2 = dry<br>3 = fan<br>4 = heat</p> |
|   | bit 5 : reset "clean filter" message |
| 5 | <p>bit 7-0 : on/off<br>c4 = switch off<br>f4 = switch on</p> |
| 6 | 0 |
| 7 | <p>bit 3-0 : set blade position<br>0 = closed<br>1 = open smallest<br>2 = mid positions<br>7 = open max</p> |
|   | bit 4 : set blade position |
|   | bit 5 : quiet mode |
| 8 | 0 |

| Cmd | Description |
| :---: | :--- |
| 52  | Reply  |

| Data byte | Settings |
| :---: | :--- |
| 1 | bit 4-0 : set temperature - 9 |
| 2 | bit 4-0 : room temperature - 9 |
| 3 | temperature ? |
| 4 | <p>bit 2-0 : fan speed<br>0 = auto<br>2 = low<br>4 = medium<br>5 = high</p> |
|   | <p>bit 7-3 : blade swing<br>1A = swing up/down<br>1F = blade swing off</p> |


## Tools
To snif the communication protocol I used a Raspberry Pi and a RS485 -> TTL convertor which you can easily find on e-bay (search for: TTL RS485 Adapter 485 UART Seriell 3.3V 5 Volt Level Konverter Modul Arduino). Although I had the impression that the RS-485 driver was not working well on 3.3V, I replaced it with following driver : SN65HVD11D from Texas Instruments. I connected the 2 RS-485 wires from the indoor unit to the convertor, the convertor is connected to the Pi's rx and tx pins of the IO header. Be aware the the TTL levels must be 3.3V compatible, if they are 5V, the Pi's IO's will be damaged.

I made some Python scripts to display all the information coming from the serial comms in a meaningful manner.
Pyserial is a required package.

Call the scripts with the -h option to obtain info on how to use it.
serial_dump.py dumps all serial communication on screen, there is no transmission of commands.
lib_serial.py is used by ac_control.py 

In my setup, I use the wired remote control in combination with the Raspberry Pi which acts also as a master. This makes the communication a bit tricky. The wired remote control sends commands to all units in sequence and ends the communication with a command to destination address 0xAD, no reply is coming from any of the units on this one. I suspect the 0xAD address to be a broadcast address. Then there is a 300 ms gap in the communication and then it all starts over with other commands. During this gap the tools make use of the bus to send their own commands. The wired remote will not notice the presence of the other master but it will take over the changed settings of the untis when it polls their status.
