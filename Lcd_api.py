# lcd_api.py

class LcdApi:
    # Based on the API defined at https://www.sparkfun.com/datasheets/LCD/HD44780.pdf

    # The following constant names are from the document

    # Commands
    LCD_CLR = 0x01              # DB0: clear display
    LCD_HOME = 0x02             # DB1: return to home position
    LCD_ENTRY_MODE = 0x04       # DB2: set entry mode
    LCD_DISPLAY_CTRL = 0x08     # DB3: turn lcd/cursor on
    LCD_SHIFT = 0x10            # DB4: move cursor/display
    LCD_FUNCTION_SET = 0x20     # DB5: set interface length
    LCD_CGRAM_ADDR = 0x40       # DB6: set CG RAM address
    LCD_DDRAM_ADDR = 0x80       # DB7: set DD RAM address

    # Flags for display entry mode
    ENTRY_RIGHT = 0x00          # DB2: cursor move direction
    ENTRY_LEFT = 0x02           # DB2: display shift
    ENTRY_SHIFT_INC = 0x01      # DB2: shift display when the cursor moves

    # Flags for display/cursor control
    DISPLAY_ON = 0x04           # DB3: display on
    DISPLAY_OFF = 0x00          # DB3: display off
    CURSOR_ON = 0x02            # DB3: cursor on
    CURSOR_OFF = 0x00           # DB3: cursor off
    BLINK_ON = 0x01             # DB3: blink on
    BLINK_OFF = 0x00            # DB3: blink off

    # Flags for display/cursor shift
    DISPLAY_MOVE = 0x08         # DB4: move display
    CURSOR_MOVE = 0x00          # DB4: move cursor
    MOVE_RIGHT = 0x04           # DB4: move right
    MOVE_LEFT = 0x00            # DB4: move left

    # Flags for function set
    _8_BIT_MODE = 0x10          # DB5: 8-bit mode
    _4_BIT_MODE = 0x00          # DB5: 4-bit mode
    _2_LINE = 0x08              # DB5: 2-line mode
    _1_LINE = 0x00              # DB5: 1-line mode
    _5x10_DOTS = 0x04           # DB5: 5x10 dot mode
    _5x8_DOTS = 0x00            # DB5: 5x8 dot mode

    # The first argument 'i2c' must be an I2C instance
    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.display_control = self.DISPLAY_ON
        self.display_mode = self.ENTRY_LEFT | self.ENTRY_SHIFT_INC
        self.display_function = self._4_BIT_MODE | self._2_LINE | self._5x8_DOTS

        self.current_line = 0
        self.current_column = 0

        self.init_lcd()

    def init_lcd(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def move_to(self, line, column):
        raise NotImplementedError

    def putchar(self, char):
        raise NotImplementedError

    def write(self, string):
        for char in string:
            self.putchar(char)
