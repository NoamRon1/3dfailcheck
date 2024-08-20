from Lcd_api import LcdApi
import time

class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr

        self.backlight = 0x08

        self.pcf8574_write(0)
        time.sleep(0.02)

        self._4bit_mode()
        self.init_lcd()

        super().__init__(num_lines, num_columns)

    def pcf8574_write(self, byte):
        self.i2c.writeto(self.i2c_addr, bytearray([byte]))

    def pulse_enable(self, byte):
        self.pcf8574_write(byte | 0x04)
        time.sleep_us(1)
        self.pcf8574_write(byte & ~0x04)
        time.sleep_us(50)

    def lcd_write_4bits(self, byte):
        byte = byte | self.backlight
        self.pcf8574_write(byte)
        self.pulse_enable(byte)

    def lcd_write(self, byte, mode=0):
        high_nibble = byte & 0xf0
        low_nibble = (byte << 4) & 0xf0

        self.lcd_write_4bits(high_nibble | mode)
        self.lcd_write_4bits(low_nibble | mode)

    def init_lcd(self):
        self.lcd_write(self.LCD_FUNCTION_SET | self.display_function)
        self.lcd_write(self.LCD_DISPLAY_CTRL | self.display_control)
        self.clear()
        self.lcd_write(self.LCD_ENTRY_MODE | self.display_mode)

    def clear(self):
        self.lcd_write(self.LCD_CLR)
        time.sleep_ms(2)

    def move_to(self, line, column):
        if line > self.num_lines or column > self.num_columns:
            return

        self.current_line = line
        self.current_column = column
        self.lcd_write(self.LCD_DDRAM_ADDR | (line << 6) | column)

    def putchar(self, char):
        self.lcd_write(ord(char), 0x01)
