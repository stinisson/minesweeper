from constants import ROWS, COLS, SQUARE_WIDTH, SQUARE_HEIGHT, PIXEL_X, PIXEL_Y


def value_in_range(measured_color, expected_color, offset):
    """ Return True if the squares' rgb value is within expected_color +- offset"""
    for idx, value in enumerate(measured_color):
        if not expected_color[idx] - offset <= value <= expected_color[idx] + offset:
            return False
    return True


def read_values_from_board(im):
    board_values = []
    print("")
    for row in range(ROWS):
        for col in range(COLS):
            print("| ", end="")
            col_coord = PIXEL_X + col * SQUARE_WIDTH
            row_coord = PIXEL_Y + row * SQUARE_HEIGHT
            rgb_value = im.getpixel((col_coord, row_coord))

            col_coord_frame = 2 + col * SQUARE_WIDTH  # Color of unclicked squares overlaps with clicked
            row_coord_frame = 2 + row * SQUARE_HEIGHT  # Use rgb value of frame for unclicked squares
            rgb_value_frame = im.getpixel((col_coord_frame, row_coord_frame))

            if value_in_range(rgb_value, (9, 9, 130), 9):
                value = "1"
            elif value_in_range(rgb_value, (4, 129, 4), 4):
                value = "2"
            elif value_in_range(rgb_value, (128, 102, 0), 2):
                value = "3"
            elif value_in_range(rgb_value, (105, 27, 88), 2):
                value = "4"
            elif value_in_range(rgb_value, (189, 3, 3), 2):
                value = "5"
            elif value_in_range(rgb_value, (140, 0, 0), 4):
                value = "6"
            elif value_in_range(rgb_value, (62, 62, 62), 8):
                value = "8"
            elif value_in_range(rgb_value, (27, 27, 27), 4):
                value = "M"  # Mine found
            elif value_in_range(rgb_value_frame, (220, 220, 220), 3):
                rgb_value_flag = im.getpixel((col * SQUARE_WIDTH + 8, row * SQUARE_HEIGHT + 8))
                if value_in_range(rgb_value_flag, (170, 49, 49), 5):
                    value = "F"  # Flag
                else:
                    value = "-"  # not-clicked
            elif value_in_range(rgb_value, (185, 185, 185), 15):
                value = "x"  # clicked
            else:
                rgb_value_seven = im.getpixel((col_coord - 3, row_coord))  # Seven is a special case
                if value_in_range(rgb_value_seven, (181, 92, 6), 5):       # todo: use a single pixel location
                    value = "7"
                else:
                    value = "U"  # unknown
                    #print("Unknown rgb:", rgb_value)
            board_values.append(value)
            print(value, end=" ")
        print("|")

    return board_values
