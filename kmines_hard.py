import pyautogui
import glob

files = [int(f[-7:-4]) for f in glob.glob("screenshots/*.png")]
if files:
    latest_file_ending = max(files)
    file_ending = str(latest_file_ending + 1).zfill(4)
else:
    file_ending = "0000"

im = pyautogui.screenshot()
locator_location = pyautogui.locateOnScreen('img/locator.png', confidence=0.9)

if locator_location is not None:

    # Start a new game
    locatorpoint = pyautogui.center(locator_location)
    pyautogui.click(locatorpoint.x, locatorpoint.y)

    # if game ended, quit game
    game_ended = pyautogui.locateOnScreen('img/game_ended.png', confidence=0.9)
    if game_ended:
        print("Oh noes, a mine got clicked! \n Game ended.")
        quit()

    # Upper left matrix from locator top left (204, 67)
    # Bottom right matrix from locator top left (528, 391)
    #WIDTH = 528 - 204
    #HEIGHT = 391 - 67

    # Upper left matrix from locator top left (36, 53)
    # Bottom right matrix from locator top left (695, 404)
    WIDTH = 695 - 36
    HEIGHT = 404 - 53

    TOP_LEFT = (locator_location.left + 36, locator_location.top + 53)
    BOT_RIGHT = (695, 404)

    SQUARE_WIDTH = SQUARE_HEIGHT = 22
    rc00 = TOP_LEFT[0] + SQUARE_WIDTH/2, TOP_LEFT[1] + SQUARE_HEIGHT/2
    pyautogui.click(rc00[0], rc00[1])
    print("Clicked first square", rc00[0], rc00[1])
    im2 = pyautogui.screenshot(f"screenshots/screenshot_{file_ending}.png", region=(TOP_LEFT[0], TOP_LEFT[1], WIDTH, HEIGHT))

    ROWS = 16
    COLS = 30

    PIXEL_X = 12
    PIXEL_Y = 17

    coordinates = {}

    print("TOP LEFT", TOP_LEFT)
    print("(row, col)")
    for row in range(ROWS):
        for col in range(COLS):
            #col_coord = SQUARE_WIDTH//2 + col * SQUARE_WIDTH
            #row_coord = SQUARE_HEIGHT//2 + row * SQUARE_HEIGHT

            col_coord = PIXEL_X + col * SQUARE_WIDTH
            row_coord = PIXEL_Y + row * SQUARE_HEIGHT

            rgb_pixel = im2.getpixel((col_coord, row_coord))
            #print(f"({row}, {col}): {rgb_pixel}")

            position = f"rc{row}-{col}"
            square = ""
            if rgb_pixel == (193, 193, 193) or rgb_pixel == (194, 194, 194) or rgb_pixel == (191, 191, 191) \
                    or rgb_pixel == (193, 193, 194) or rgb_pixel == (189, 189, 189) or rgb_pixel == (187, 187, 187):
                square = "clicked"
            elif rgb_pixel == (4, 4, 130):
                square = "blue 1"
            elif rgb_pixel == (1, 129, 1):
                square = "green 2"
            elif rgb_pixel == (128, 102, 0):
                square = "gold 3"
            elif rgb_pixel == (105, 27, 88):
                square = "purple 4"
            elif rgb_pixel == (181, 181, 181) or rgb_pixel == (183, 183, 183):
                square = "unclicked"
            else:
                square = "UNKNOWN"
            coordinates[position] = (rgb_pixel, square)

    for coord in coordinates:
        print(coord, coordinates[coord])
else:
    print("Could not locate minesweeper window.")
