from constants import ROWS, COLS, SQUARE_WIDTH, SQUARE_HEIGHT, OFFS_NUMBERS, OFFS_SEVEN, OFFS_FLAG, OFFS_UNOPENED


def color_in_range(measured_color, expected_color, offset):
    """ Return True if the rgb value is within expected_color +- offset """
    for idx, value in enumerate(measured_color):
        if not expected_color[idx] - offset <= value <= expected_color[idx] + offset:
            return False
    return True


def read_board_state(im):
    """ Read board state from screenshot and return a list of values of the current game state.
        Possible values:
        "1"-"8": square numbers depicting number of neighbouring mines,
        "F": flagged mine, "M": mine, "-": unopened square, "x": opened square, "U": unknown."""
    board = []
    for row in range(ROWS):
        for col in range(COLS):
            print("| ", end="")
            col_origo, row_origo = col * SQUARE_WIDTH, row * SQUARE_HEIGHT

            rgb_value = im.getpixel((OFFS_NUMBERS[0] + col_origo, OFFS_NUMBERS[1] + row_origo))
            rgb_value_seven = im.getpixel((OFFS_SEVEN[0] + col_origo, OFFS_SEVEN[1] + row_origo))
            rgb_value_frame = im.getpixel((OFFS_UNOPENED[0] + col_origo, OFFS_UNOPENED[1] + row_origo))
            rgb_value_flag = im.getpixel((OFFS_FLAG[0] + col_origo, OFFS_FLAG[1] + row_origo))

            if color_in_range(rgb_value, (9, 9, 130), 9):
                value = "1"
            elif color_in_range(rgb_value, (4, 129, 4), 4):
                value = "2"
            elif color_in_range(rgb_value, (128, 102, 0), 2):
                value = "3"
            elif color_in_range(rgb_value, (105, 27, 88), 2):
                value = "4"
            elif color_in_range(rgb_value, (189, 3, 3), 2):
                value = "5"
            elif color_in_range(rgb_value, (140, 0, 0), 4):
                value = "6"
            elif color_in_range(rgb_value_seven, (181, 92, 6), 5):
                # todo: seven is a special case, find common pixel location for all numbers
                value = "7"
            elif color_in_range(rgb_value, (62, 62, 62), 8):
                value = "8"
            elif color_in_range(rgb_value, (27, 27, 27), 4):
                value = "M"
            elif color_in_range(rgb_value_flag, (170, 49, 49), 5):
                value = "F"
            elif color_in_range(rgb_value_frame, (220, 220, 220), 3):
                value = "-"  # not-clicked
            elif color_in_range(rgb_value, (185, 185, 185), 15):
                value = "x"  # clicked
            else:
                value = "U"  # unknown
            board.append(value)
            print(value, end=" ")
        print("|")
    return board
