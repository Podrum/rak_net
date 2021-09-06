################################################################################
#                                                                              #
#  ____           _                                                            #
# |  _ \ ___   __| |_ __ _   _ _ __ ___                                        #
# | |_) / _ \ / _` | '__| | | | '_ ` _ \                                       #
# |  __/ (_) | (_| | |  | |_| | | | | | |                                      #
# |_|   \___/ \__,_|_|   \__,_|_| |_| |_|                                      #
#                                                                              #
# Copyright 2021 Podrum Studios                                                #
#                                                                              #
# Permission is hereby granted, free of charge, to any person                  #
# obtaining a copy of this software and associated documentation               #
# files (the "Software"), to deal in the Software without restriction,         #
# including without limitation the rights to use, copy, modify, merge,         #
# publish, distribute, sublicense, and/or sell copies of the Software,         #
# and to permit persons to whom the Software is furnished to do so,            #
# subject to the following conditions:                                         #
#                                                                              #
# The above copyright notice and this permission notice shall be included      #
# in all copies or substantial portions of the Software.                       #
#                                                                              #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR   #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,     #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER       #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING      #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS #
# IN THE SOFTWARE.                                                             #
#                                                                              #
################################################################################

class ProtocolInfo:
    # RakNet Offline Message ID
    MAGIC: bytes = b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78"
    # RakNet Packet IDs
    ONLINE_PING: int = 0x00
    OFFLINE_PING: int = 0x01
    OFFLINE_PING_OPEN_CONNECTIONS: int = 0x02
    ONLINE_PONG: int = 0x03
    OPEN_CONNECTION_REQUEST_1: int = 0x05
    OPEN_CONNECTION_REPLY_1: int = 0x06
    OPEN_CONNECTION_REQUEST_2: int = 0x07
    OPEN_CONNECTION_REPLY_2: int = 0x08
    CONNECTION_REQUEST: int = 0x09
    CONNECTION_REQUEST_ACCEPTED: int = 0x10
    NEW_INCOMING_CONNECTION: int = 0x13
    DISCONNECT: int = 0x15
    INCOMPATIBLE_PROTOCOL_VERSION: int = 0x19
    OFFLINE_PONG: int = 0x1c
    FRAME_SET: int = 0x80
    NACK: int = 0xa0
    ACK: int = 0xc0
