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

from binary_utils.binary_stream import binary_stream
from rak_net.utils.reliability_tool import ReliabilityTool


class Frame(binary_stream):
    def __init__(self, data: bytes = b"", pos: int = 0):
        super().__init__(data, pos)
        self.reliability: int = 0
        self.fragmented: bool = False
        self.reliable_frame_index: int = 0
        self.sequenced_frame_index: int = 0
        self.ordered_frame_index: int = 0
        self.order_channel: int = 0
        self.compound_size: int = 0
        self.compound_id: int = 0
        self.index: int = 0
        self.body: bytes = b""
    
    def decode(self) -> None:
        flags: int = self.read_unsigned_byte()
        self.reliability = (flags & 0xf4) >> 5
        self.fragmented = (flags & 0x10) > 0
        body_length: int = self.read_unsigned_short_be() >> 3
        if ReliabilityTool.reliable(self.reliability):
            self.reliable_frame_index = self.read_unsigned_triad_le()
        if ReliabilityTool.sequenced(self.reliability):
            self.sequenced_frame_index = self.read_unsigned_triad_le()
        if ReliabilityTool.sequenced_or_ordered(self.reliability):
            self.ordered_frame_index = self.read_unsigned_triad_le()
            self.order_channel = self.read_unsigned_byte()
        if self.fragmented:
            self.compound_size = self.read_unsigned_int_be()
            self.compound_id = self.read_unsigned_short_be()
            self.index = self.read_unsigned_int_be()
        self.body = self.read(body_length)
    
    def encode(self) -> None:
        self.write_unsigned_byte((self.reliability << 5) | (0x10 if self.fragmented else 0))
        self.write_unsigned_short_be(len(self.body) << 3)
        if ReliabilityTool.reliable(self.reliability):
            self.write_unsigned_triad_le(self.reliable_frame_index)
        if ReliabilityTool.sequenced(self.reliability):
            self.write_unsigned_triad_le(self.sequenced_frame_index)
        if ReliabilityTool.sequenced_or_ordered(self.reliability):
            self.write_unsigned_triad_le(self.ordered_frame_index)
            self.write_unsigned_byte(self.order_channel)
        if self.fragmented:
            self.write_unsigned_int_be(self.compound_size)
            self.write_unsigned_short_be(self.compound_id)
            self.write_unsigned_int_be(self.index)
        self.write(self.body)
        
    def get_size(self) -> int:
        length: int = 3
        if ReliabilityTool.reliable(self.reliability):
            length += 3
        if ReliabilityTool.sequenced(self.reliability):
            length += 3
        if ReliabilityTool.sequenced_or_ordered(self.reliability):
            length += 4
        if self.fragmented:
            length += 10
        length += len(self.body)
        return length
