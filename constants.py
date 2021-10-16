TOTAL_NUM_MINES = 99                    # Level: hard, theme: default (oxygen)
COLS, ROWS = 30, 16
SQUARE_WIDTH = SQUARE_HEIGHT = 22       # (setup_board_size_with_gimp_square_width_height.png)
WIDTH, HEIGHT = COLS * SQUARE_WIDTH, ROWS * SQUARE_HEIGHT
BOARD_LEFT_TOP = (34, 53)               # Must be measured (setup_board_size_with_gimp.png)

OFFS_NUMBERS = (12, 17)   # Where to look for number color in square, assuming square size 22
OFFS_SEVEN = (9, 17)      # Number seven doesn't overlap with the other numbers
OFFS_UNOPENED = (2, 2)    # Color of unopened squares overlaps with opened, use rgb value of frame for unopened squares
OFFS_FLAG = (8, 8)
