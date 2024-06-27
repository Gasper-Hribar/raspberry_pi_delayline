class DelayLine():


    def method_0(self, arguments):
        return


    def __init__(self):
        return


class NOCHIP(DelayLine):
    """
    No chip is selected. Initialized at the start of the program.
    """

    name = "nochip"

    def get_name(self):
        return self.name

class SY89297U(DelayLine):
    """
    SY89297 chip object definition.
    """

    name = "SY89297U"


    def reverse_bits_10bit(self, number):
        reversed_number = 0
        for _ in range(10):  # For a 10-bit number
            reversed_number = (reversed_number << 1) | (number & 1)
            number >>= 1
        return reversed_number


    def calc_delay(self, value, unit):
        # print("calc")
        if unit:
            value = value * 1000

        result = (value + self.correction[value % 5]) / 5
        return result

    def define_latch_A(self, value):
        # print("latch a")
        value = self.reverse_bits_10bit(int(value))
        return value
    
    def define_latch_B(self, value):
        # print("latch b")
        value = self.reverse_bits_10bit(int(value))
        return value
    
    def get_name(self):
        return self.name
    
    def __init__(self):
        # super().__init__()
        self.correction = [0, -1, -2, 2, 1]
        return


class MCP23S17(DelayLine):
    """
    MCP23S17 chip object definition.

    MCP23S17 is used to set two MC100EP195B delay line chips.
    """

    name = "MCP23S17"

    # registers of the MCP

    IOCON_BANK = 0

    IODIRA = 0b00000000
    IODIRB = 0b00000001
    IPOLA = 0b00000010
    IPOLB = 0b00000011
    GPINTENA = 0b00000100
    GPINTENB = 0b00000101
    DEFVALA = 0b00000110
    DEFVALB = 0b00000111
    INTCONA = 0b00001000
    INTCONB = 0b00001001
    IOCONA = 0b00001010
    IOCONB = 0b00001011
    GPPUA = 0b00001100
    GPPUB = 0b00001101
    INTFA = 0b00001110
    INFTB = 0b00001111
    INTCAPA = 0b00010000
    INTCAPB = 0b00010001
    GPIOA = 0b00010010
    GPIOB = 0b00010011
    OLATA = 0b00010100
    OLATB = 0b00010101

    if IOCON_BANK == 1:

        IODIRA = 0b00000000
        IODIRB = 0b00010000
        IPOLA = 0b00000001
        IPOLB = 0b00010001
        GPINTENA = 0b00000010
        GPINTENB = 0b00010010
        DEFVALA = 0b00000011
        DEFVALB = 0b00010011
        INTCONA = 0b00000100
        INTCONB = 0b00010100
        IOCONA = 0b00000101
        IOCONB = 0b00010101
        GPPUA = 0b00000110
        GPPUB = 0b00010110
        INTFA = 0b00000111
        INFTB = 0b00010111
        INTCAPA = 0b00001000
        INTCAPB = 0b00011000
        GPIOA = 0b00001001
        GPIOB = 0b00011001
        OLATA = 0b00011010
        OLATB = 0b00011010

    # MSB bits definitions for SY100EP195V
    SEL0_BIT = 14
    SEL1_BIT = 15
    LEN0_BIT = 12
    LEN1_BIT = 13
    EN_BIT = 11


    def get_name(self):
        return self.name
    
    def makeAddressable(self):
        """
        Returns the values to write via SPI to mak the MCP addressable by HAD.
        """

        value =[0b01000000 | self.address << 1, 
                MCP23S17.IOCONA | 1 << 3
            ]
        return value
    
    def setIO(self):
        """
        Returns a data packet to set all of GPIOs on MCP chip to outputs.
        """

        value = [0b01000000 | self.address << 1,
                 0b00000000,
                 0b00000000,
                 0b00000000
                 ]  # value: first byte = address, second byte = 0, third and fourth bytes = bits for setting I/O (output = 0)
        return value
    
    
    def set_bits(self, en, s0, s1):
        retval = 1 << MCP23S17.LEN0_BIT | 1 << MCP23S17.LEN1_BIT

        first_byte = 0b01000000 | self.address << 1
        second_byte = MCP23S17.GPIOA
        third_byte = 0
        fourth_byte = en << 3 | s0 << 6 | s1 << 7

        return [first_byte, second_byte, third_byte, fourth_byte]
    

    def calc_delay(self, value, unit, side, enable, sel0, sel1):
        """
        Returns a value to write to the MCP to forward it to the SZ100EP195B (V).

        Step of the programmable delay is 10 ps (12230 - 2000) / 2**10. 
        """
        
        ps_value = value * 1000 if unit else value
        retval = int(ps_value / 10) & 1023
        retval = retval | 1 << MCP23S17.LEN0_BIT | 1 << MCP23S17.LEN1_BIT 
        # print(f"Retval: {retval}, {bin(retval)}.")

        if side == 0:
            retval_latch = retval & (2**16 - 1 - 2**MCP23S17.LEN0_BIT)
            # print(f"Retval latch: {retval_latch}, {bin(retval_latch)}.") 
        else:
            retval_latch = retval & (2**16 - 1 - 2**MCP23S17.LEN1_BIT)
            # print(f"Retval latch: {retval_latch}, {bin(retval_latch)}.")

        address_byte = 0b01000000 | self.address << 1
        register_byte = MCP23S17.GPIOA
        data_byte_3 = (retval >> 8) & 255 | enable << 3 | sel0 << 6 | sel1 << 7
        data_byte_2 = retval & 255
        data_byte_1 = (retval_latch >> 8) & 255 | enable << 3 | sel0 << 6 | sel1 << 7
        data_byte_0 = retval_latch & 255
        
        return [address_byte, register_byte, data_byte_0, data_byte_1, address_byte, register_byte, data_byte_2, data_byte_3]
       

    def __init__(self, address):
        # super().__init__()
        self.address = address