import pyautogui
from datetime import datetime
import mss
from PIL import Image

from constants import ROWS, COLS, SQUARE_WIDTH, SQUARE_HEIGHT, WIDTH, HEIGHT, NUM_MINES, BOARD_LEFT_TOP
from read_board_values import read_values_from_board


def setup():
    locator_location = pyautogui.locateOnScreen('img/locator.png', confidence=0.9)
    if locator_location is not None:
        locator_point = pyautogui.center(locator_location)
        pyautogui.click(locator_point.x, locator_point.y)
        board_origo = (locator_location[0] + BOARD_LEFT_TOP[0], locator_location[1] + BOARD_LEFT_TOP[1])
        return board_origo
    else:
        print("Couldn't locate 'New' button. Make sure it's visible on the screen. ")
        quit()


def reset_game():
    reset_button_location = pyautogui.locateOnScreen('img/reset_game_locator.png', confidence=0.9)
    if reset_button_location:
        locator_point = pyautogui.center(reset_button_location)
        pyautogui.click(locator_point.x, locator_point.y)
        print("Resetting game!")


def game_won_displayed():
    high_score_location = pyautogui.locateOnScreen('img/win.png', confidence=0.9)
    if high_score_location:
        print("Game won! :)")
        return True
    return False


def run_game():
    reset_game()
    board_origo = setup()
    probabilities = []
    flag_count = 0

    while True:
        print(f" \n-------------------------------- OPEN SQUARE ---------------------------------")
        if len(probabilities) == 0:
            click_square(row=0, col=0, button='left', board_origo=board_origo)
        else:
            temp_probabilities = [prob for prob in probabilities if prob not in ["-xx-", "-mm-"]]
            lowest_probability = min(temp_probabilities)
            lowest_prob_idx = probabilities.index(lowest_probability)

            row = lowest_prob_idx // COLS
            col = lowest_prob_idx % COLS
            click_square(row=row, col=col, button='left', board_origo=board_origo)

        im = take_board_screenshot(board_origo)
        board = read_values_from_board(im)

        if 'U' in board:   # A board value that isn't recognized is marked as U (unknown), stop game if U appear
            break

        if 'M' in board:
            print("Oh noes, a mine was clicked!")
            break
        if any(x in board for x in ['7', '8']):
            take_unicorn_screenshot("unicorn_number", board_origo)

        square_numbers = square_numbers_on_board(board)

        while True:
            calculate_base_probabilities(board, probabilities)
            update_square_number_probabilities(square_numbers, probabilities, board)
            if not mark_mine_with_flag(probabilities, board, board_origo=board_origo):
                break
            flag_count += 1

        print("Flag count", flag_count)
        if flag_count == NUM_MINES:
            # If all mines are flagged but squares are still unclicked they must be opened in order to finish the game
            while '-' in board:
                mine_idx = board.index('-')
                click_square(row=mine_idx // COLS, col=mine_idx % COLS, button='left', board_origo=board_origo)
                if game_won_displayed():   # If High Score is displayed - quit game
                    break
                im = take_board_screenshot(board_origo)
                board = read_values_from_board(im)
            quit()

        # Useful during test run
        show_probability_matrix(probabilities)
        print_result(board)


def print_result(board_values):
    print("\n----  Result  ----")
    print("Mines left:", NUM_MINES - board_values.count('F'))
    print("Squares left:", board_values.count('-'))


def calculate_base_probabilities(board_values, probabilities):
    probabilities.clear()
    candidates = board_values.count('-')
    num_mines_left = NUM_MINES - board_values.count('F')

    for row in range(ROWS):
        for col in range(COLS):
            idx = col + row * COLS
            if board_values[idx] == '-':
                prob = round(num_mines_left / candidates, 2)
                probabilities.append(prob)
            elif board_values[idx] == 'F':
                prob = "-mm-"
                probabilities.append(prob)
            else:
                prob = "-xx-"
                probabilities.append(prob)


def calc_square_number_probabilities(square_number, neighbours_idx, board_values):
    num_mines = 0
    num_candidates = 0
    for idx in neighbours_idx:
        if board_values[idx] == 'F':
            num_mines += 1
        elif board_values[idx] == '-':
            num_candidates += 1
    prob = 0
    neighbour_probabilities = []
    if num_candidates > 0:
        prob = max(0.0, (square_number - num_mines) / num_candidates)

    for neighbour_idx in neighbours_idx:
        if board_values[neighbour_idx] == '-':
            neighbour_probabilities.append(round(prob, 2))
        else:
            neighbour_probabilities.append('-.-')
    return neighbour_probabilities


def update_square_number_probabilities(square_numbers, probabilities, board_values):
    for square_num_idx in square_numbers:  # {value index: number value}
        curr_row = square_num_idx // COLS
        curr_col = square_num_idx % COLS

        neighbour_pos = {'tl': (curr_col - 1, curr_row - 1), 'tm': (curr_col, curr_row - 1),
                         'tr': (curr_col + 1, curr_row - 1),
                         'l': (curr_col - 1, curr_row), 'm': (curr_col, curr_row), 'r': (curr_col + 1, curr_row),
                         'bl': (curr_col - 1, curr_row + 1), 'bm': (curr_col, curr_row + 1),
                         'br': (curr_col + 1, curr_row + 1)}

        neighbours_idx = []
        for pos in neighbour_pos:
            col, row = neighbour_pos[pos]
            if 0 <= row < ROWS and 0 <= col < COLS:
                idx = col + row * COLS
                neighbours_idx.append(idx)  # Add index of neighbours_idx

        neighbour_probabilities = calc_square_number_probabilities(int(square_numbers[square_num_idx]),
                                                                   neighbours_idx, board_values)

        for idx, neigh_idx in enumerate(neighbours_idx):
            base_prob = probabilities[neigh_idx]
            neigh_prob = neighbour_probabilities[idx]
            if neigh_prob != "-.-" and base_prob != "-mm-" and base_prob != 0.0:
                if neigh_prob > base_prob or neigh_prob == 0.0:  # Add the probability with highest mine likelihood
                    probabilities[neigh_idx] = neigh_prob


def mark_mine_with_flag(probabilities, board_values, board_origo):
    mine_indices = [i for i, prob in enumerate(probabilities) if prob == 1.00]
    for mine_idx in mine_indices:
        if board_values[mine_idx] == 'F':
            continue
        row_ = mine_idx // COLS
        col_ = mine_idx % COLS
        click_square(row=row_, col=col_, button='right', board_origo=board_origo)
        set_mine_in_probabilities(probabilities, row_, col_)
        board_values[mine_idx] = 'F'
        if board_values.count('F') == NUM_MINES:
            take_unicorn_screenshot("all_mines_flagged", board_origo=board_origo)
        return True
    return False


def set_mine_in_probabilities(probabilities, row, col):
    idx = col + row * COLS
    probabilities[idx] = "-mm-"


def show_probability_matrix(probabilities):
    print("\n\nProbability matrix")
    for idx, prob in enumerate(probabilities, start=1):
        if idx % COLS:
            if isinstance(prob, str):
                print(prob, end=" ")
            else:
                print(format(prob, '.2f'), end=" ")
        else:
            if isinstance(prob, str):
                print(prob, end="\n")
            else:
                print(format(prob, '.2f'), end="\n")


def click_square(row, col, button, board_origo):
    if not (0 <= row <= ROWS and 0 <= col <= COLS):
        return
    col_coord = board_origo[0] + SQUARE_WIDTH / 2 + col * SQUARE_WIDTH
    row_coord = board_origo[1] + SQUARE_HEIGHT / 2 + row * SQUARE_HEIGHT
    pyautogui.click(x=col_coord, y=row_coord, button=button)


def square_numbers_on_board(board_values):
    square_numbers = {}
    for idx in range(len(board_values)):
        if board_values[idx] in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            square_numbers[idx] = board_values[idx]  # {value index: number value}
    return square_numbers


def take_board_screenshot(board_origo):
    with mss.mss() as sct:
        monitor = {
            'top': board_origo[1],
            'left': board_origo[0],
            'width': WIDTH,
            'height': HEIGHT
        }
        sct_img = sct.grab(monitor)
        im = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    return im


def take_unicorn_screenshot(unicorn, board_origo):
    # If a 7 or 8 occur on the board, or all mines are flagged - take a screenshot
    # 7 and 8 are rare numbers, as is a round where all mines are flagged
    timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    file_ending = f"{unicorn}__{timestamp}"
    pyautogui.screenshot(f"screenshots/screenshot_{file_ending}.png",
                         region=(board_origo[0], board_origo[1], WIDTH, HEIGHT))
