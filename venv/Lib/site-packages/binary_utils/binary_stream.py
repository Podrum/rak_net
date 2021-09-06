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

from binary_utils.binary_converter import binary_converter

class binary_stream:
    def __init__(self, data: bytes = b"", pos: int = 0) -> None:
        self.data: bytes = data
        self.pos: int = pos
        
    def read(self, size: int) -> bytes:
        self.pos += size
        return self.data[self.pos - size:self.pos]
      
    def write(self, data: bytes) -> None:
        self.data += data
        
    def read_remaining(self) -> bytes:
        return self.read(len(self.data) - self.pos)
    
    def feos(self) -> bool:
        return bool(len(self.data) <= self.pos)
        
    def read_byte(self) -> int:
        return binary_converter.read_byte(self.read(1))
    
    def write_byte(self, value: int) -> None:
        self.write(binary_converter.write_byte(value))
        
    def read_unsigned_byte(self) -> int:
        return binary_converter.read_unsigned_byte(self.read(1))
    
    def write_unsigned_byte(self, value: int) -> None:
        self.write(binary_converter.write_unsigned_byte(value))
        
    def read_bool(self) -> bool:
        return binary_converter.read_bool(self.read(1))
    
    def write_bool(self, value: bool) -> None:
        self.write(binary_converter.write_bool(value))
        
    def read_short_be(self) -> int:
        return binary_converter.read_short_be(self.read(2))
    
    def write_short_be(self, value: int) -> None:
        self.write(binary_converter.write_short_be(value))
        
    def read_unsigned_short_be(self) -> int:
        return binary_converter.read_unsigned_short_be(self.read(2))
    
    def write_unsigned_short_be(self, value: int) -> None:
        self.write(binary_converter.write_unsigned_short_be(value))
        
    def read_short_le(self) -> int:
        return binary_converter.read_short_le(self.read(2))
    
    def write_short_le(self, value: int) -> None:
        self.write(binary_converter.write_short_le(value))
        
    def read_unsigned_short_le(self) -> int:
        return binary_converter.read_unsigned_short_le(self.read(2))
    
    def write_unsigned_short_le(self, value: int) -> None:
        self.write(binary_converter.write_unsigned_short_le(value))

    def read_triad_be(self) -> int:
        return binary_converter.read_triad_be(self.read(3))
    
    def write_triad_be(self, value: int) -> None:
        self.write(binary_converter.write_triad_be(value))
        
    def read_unsigned_triad_be(self) -> int:
        return binary_converter.read_unsigned_triad_be(self.read(3))
    
    def write_unsigned_triad_be(self, value: int) -> None:
        self.write(binary_converter.write_unsigned_triad_be(value))
        
    def read_triad_le(self) -> int:
        return binary_converter.read_triad_le(self.read(3))
    
    def write_triad_le(self, value: int) -> None:
        self.write(binary_converter.write_triad_le(value))
        
    def read_unsigned_triad_le(self) -> int:
        return binary_converter.read_unsigned_triad_le(self.read(3))
    
    def write_unsigned_triad_le(self, value: int) -> None:
        self.write(binary_converter.write_unsigned_triad_le(value))
        
    def read_int_be(self) -> int:
        return binary_converter.read_int_be(self.read(4))
    
    def write_int_be(self, value: int) -> None:
        self.write(binary_converter.write_int_be(value))
        
    def read_unsigned_int_be(self) -> int:
        return binary_converter.read_unsigned_int_be(self.read(4))
    
    def write_unsigned_int_be(self, value: int) -> None:
        self.write(binary_converter.write_unsigned_int_be(value))
        
    def read_int_le(self) -> int:
        return binary_converter.read_int_le(self.read(4))
    
    def write_int_le(self, value: int) -> None:
        self.write(binary_converter.write_int_le(value))
        
    def read_unsigned_int_le(self) -> int:
        return binary_converter.read_unsigned_int_le(self.read(4))
    
    def write_unsigned_int_le(self, value: int) -> None:
        self.write(binary_converter.write_unsigned_int_le(value))

    def read_long_be(self) -> int:
        return binary_converter.read_long_be(self.read(8))
    
    def write_long_be(self, value: int) -> None:
        self.write(binary_converter.write_long_be(value))
        
    def read_unsigned_long_be(self) -> int:
        return binary_converter.read_unsigned_long_be(self.read(8))
    
    def write_unsigned_long_be(self, value: int) -> None:
        self.write(binary_converter.write_unsigned_long_be(value))
        
    def read_long_le(self) -> int:
        return binary_converter.read_long_le(self.read(8))
    
    def write_long_le(self, value: int) -> None:
        self.write(binary_converter.write_long_le(value))
        
    def read_unsigned_long_le(self) -> int:
        return binary_converter.read_unsigned_long_le(self.read(8))
    
    def write_unsigned_long_le(self, value: int) -> None:
        self.write(binary_converter.write_unsigned_long_le(value))
        
    def read_float_be(self) -> int:
        return binary_converter.read_float_be(self.read(4))
    
    def write_float_be(self, value: int) -> None:
        self.write(binary_converter.write_float_be(value))
        
    def read_float_le(self) -> int:
        return binary_converter.read_float_le(self.read(4))
    
    def write_float_le(self, value: int) -> None:
        self.write(binary_converter.write_float_le(value))
        
    def read_double_be(self) -> int:
        return binary_converter.read_double_be(self.read(8))
    
    def write_double_be(self, value: int) -> None:
        self.write(binary_converter.write_double_be(value))
        
    def read_double_le(self) -> int:
        return binary_converter.read_double_le(self.read(8))
    
    def write_double_le(self, value: int) -> None:
        self.write(binary_converter.write_double_le(value))
        
    def read_var_int(self) -> int:
        value: int = 0
        for i in range(0, 35, 7):
            if self.feos():
                raise Exception("Data position exceeded")
            number: int = self.read_unsigned_byte()
            value |= ((number & 0x7f) << i)
            if (number & 0x80) == 0:
                return value
        raise Exception("VarInt is too big")
            
    def write_var_int(self, value: int) -> None:
        data: bytes = b""
        value &= 0xffffffff
        for i in range(0, 5):
            to_write: int = value & 0x7f
            value >>= 7
            if value != 0:
                self.write_unsigned_byte(to_write | 0x80)
            else:
                self.write_unsigned_byte(to_write)
                break
                
    def read_signed_var_int(self) -> int:
        raw: int = self.read_var_int()
        temp: int = -(raw >> 1) - 1 if (raw & 1) else raw >> 1
        return temp
    
    def write_signed_var_int(self, value: int) -> None:
        self.write_var_int(value << 1 if value >= 0 else (-value - 1) << 1 | 1)
            
    def read_var_long(self) -> int:
        value: int = 0
        for i in range(0, 70, 7):
            if self.feos():
                raise Exception("Data position exceeded")
            number: int = self.read_unsigned_byte()
            value |= ((number & 0x7f) << i)
            if (number & 0x80) == 0:
                return value
        raise Exception("VarLong is too big")
            
    def write_var_long(self, value: int) -> None:
        for i in range(0, 10):
            to_write: int = value & 0x7f
            value >>= 7
            if value != 0:
                self.write_unsigned_byte(to_write | 0x80)
            else:
                self.write_unsigned_byte(to_write)
                break
                
    def read_signed_var_long(self) -> int:
        raw: int = self.read_var_long()
        temp: int = -(raw >> 1) - 1 if (raw & 1) else raw >> 1
        return temp
    
    def write_signed_var_long(self, value: int) -> None:
        self.write_var_long(value << 1 if value >= 0 else (-value - 1) << 1 | 1)
