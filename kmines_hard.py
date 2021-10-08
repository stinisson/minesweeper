import pyautogui
import glob
import time

SQUARE_WIDTH = SQUARE_HEIGHT = 22
# Upper left matrix from locator top left (36, 53)
# Bottom right matrix from locator top left (695, 404)
WIDTH = 696 - 36
HEIGHT = 405 - 53

BOT_RIGHT = (696, 405)

ROWS = 16
COLS = 30

PIXEL_X = 12
PIXEL_Y = 17


def new_game():
    locator_location = pyautogui.locateOnScreen('img/locator.png', confidence=0.9)
    if locator_location is not None:
        locator_point = pyautogui.center(locator_location)
        pyautogui.click(locator_point.x, locator_point.y)
        return locator_location
    else:
        print("Couldn't locate 'New' button. Make sure it's visible on the screen")
        return None


def get_file_ending():
    files = [int(f[-7:-4]) for f in glob.glob("screenshots/*.png")]
    if files:
        latest_file_ending = max(files)
        file_ending = str(latest_file_ending + 1).zfill(4)
    else:
        file_ending = "0000"
    return file_ending


def open_first_square(top_left):
    rc00 = top_left[0] + SQUARE_WIDTH / 2, top_left[1] + SQUARE_HEIGHT / 2
    pyautogui.click(rc00[0], rc00[1])
    file_ending = get_file_ending()
    return pyautogui.screenshot(f"screenshots/screenshot_{file_ending}.png",
                                region=(top_left[0], top_left[1], WIDTH, HEIGHT))


def game_ended():
    if pyautogui.locateOnScreen('img/game_ended.png', confidence=0.9):
        print("Oh noes, a mine got clicked! \n Game ended.")
        quit()


def value_in_range(rgb_value, threshold, offset):
    """ Return True if the squares' rgb value is within the given threshold +- offset"""
    for idx, value in enumerate(rgb_value):
        if not (threshold[idx] - offset <= value <= threshold[idx] + offset):
            return False
    return True


def run_game():
    locator_location = new_game()
    if locator_location is None:
        quit()

    top_left = (locator_location.left + 36, locator_location.top + 53)
    im = open_first_square(top_left)

    coordinates = {}
    print("")
    for row in range(ROWS):
        for col in range(COLS):
            print("| ", end="")
            col_coord = PIXEL_X + col * SQUARE_WIDTH
            row_coord = PIXEL_Y + row * SQUARE_HEIGHT
            rgb_value = im.getpixel((col_coord, row_coord))

            col_coord_frame = 1 + col * SQUARE_WIDTH
            row_coord_frame = 1 + row * SQUARE_HEIGHT
            rgb_value_frame = im.getpixel((col_coord_frame, row_coord_frame))

            position = f"rc{row}-{col}"
            value = ""
            if value_in_range(rgb_value_frame, (163, 163, 163), 3):
                value = "-"  # not-clicked
            elif value_in_range(rgb_value, (185, 185, 185), 15):
                value = "x"  # clicked
            elif value_in_range(rgb_value, (4, 4, 130), 2):
                value = "1"
            elif value_in_range(rgb_value, (1, 129, 1), 2):
                value = "2"
            elif value_in_range(rgb_value, (128, 102, 0), 2):
                value = "3"
            elif value_in_range(rgb_value, (105, 27, 88), 2):
                value = "4"
            else:
                value = "U"  # unknown
                print("Unknown rgb:", rgb_value)

            coordinates[position] = (rgb_value, value)
            print(value, end=" ")
        print("|")

    for coord in coordinates:
        # print(coord, coordinates[coord])
        pass


if __name__ == '__main__':
    for i in range(1):
        run_game()
        time.sleep(3)
