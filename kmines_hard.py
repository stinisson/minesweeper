import pyautogui
import glob

SQUARE_WIDTH = SQUARE_HEIGHT = 22
# Upper left matrix from locator top left (36, 53)
# Bottom right matrix from locator top left (695, 404)
WIDTH = 695 - 36
HEIGHT = 404 - 53

BOT_RIGHT = (695, 404)

ROWS = 16
COLS = 30

PIXEL_X = 12
PIXEL_Y = 17


def new_game():
    im = pyautogui.screenshot()
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


def open_first_square(TOP_LEFT):
    rc00 = TOP_LEFT[0] + SQUARE_WIDTH / 2, TOP_LEFT[1] + SQUARE_HEIGHT / 2
    pyautogui.click(rc00[0], rc00[1])
    print("Clicked first square", rc00[0], rc00[1])

    file_ending = get_file_ending()
    return pyautogui.screenshot(f"screenshots/screenshot_{file_ending}.png",
                               region=(TOP_LEFT[0], TOP_LEFT[1], WIDTH, HEIGHT))


def game_ended():
    game_ended = pyautogui.locateOnScreen('img/game_ended.png', confidence=0.9)
    if game_ended:
        print("Oh noes, a mine got clicked! \n Game ended.")
        quit()


locator_location = new_game()
if locator_location is None:
    quit()

TOP_LEFT = (locator_location.left + 36, locator_location.top + 53)

im = open_first_square(TOP_LEFT)

coordinates = {}
for row in range(ROWS):
    #print("")
    #print("- " * 61)
    for col in range(COLS):
        print("| ", end="")
        col_coord = PIXEL_X + col * SQUARE_WIDTH
        row_coord = PIXEL_Y + row * SQUARE_HEIGHT
        rgb_pixel = im.getpixel((col_coord, row_coord))

        position = f"rc{row}-{col}"
        value = ""
        valuex = ""
        if rgb_pixel == (193, 193, 193) or rgb_pixel == (194, 194, 194) or rgb_pixel == (191, 191, 191) \
                or rgb_pixel == (193, 193, 194) or rgb_pixel == (189, 189, 189) or rgb_pixel == (187, 187, 187):
            value = "clicked"
            valuex = "x "
        elif rgb_pixel == (4, 4, 130):
            value = "blue 1"
            valuex = "1 "
        elif rgb_pixel == (1, 129, 1):
            value = "green 2"
            valuex = "2 "
        elif rgb_pixel == (128, 102, 0):
            value = "gold 3"
            valuex = "3 "
        elif rgb_pixel == (105, 27, 88):
            value = "purple 4"
            valuex = "4 "
        elif rgb_pixel == (181, 181, 181) or rgb_pixel == (183, 183, 183):
            value = "unclicked"
            valuex = "- "
        else:
            value = "UNKNOWN"
            valuex = "Z "
            print(rgb_pixel)
        print(valuex, end="")
        coordinates[position] = (rgb_pixel, value)
    print("|")

for coord in coordinates:
    #print(coord, coordinates[coord])
    pass

