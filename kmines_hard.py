from datetime import datetime
from PIL import Image
import pyautogui
import mss

from constants import ROWS, COLS, SQUARE_WIDTH, SQUARE_HEIGHT, WIDTH, HEIGHT, TOTAL_NUM_MINES, BOARD_LEFT_TOP
from read_board_state import read_board_state


def run_game(debug=False):
    reset_game()
    board_origo = setup()
    probabilities = []
    flag_count = 0

    # Click on the first square (upper left corner) to begin the game
    click_square(row=0, col=0, button='left', board_origo=board_origo)

    while True:
        if len(probabilities) > 0:
            # Click on the square with lowest probability of having a mine
            min_probability = min([prob for prob in probabilities if prob not in ["-xx-", "-mm-"]])
            min_prob_idx = probabilities.index(min_probability)
            click_square(row=min_prob_idx // COLS, col=min_prob_idx % COLS, button='left', board_origo=board_origo)

        # Take a screenshot and read the board state
        im = take_board_screenshot(board_origo)
        board = read_board_state(im)

        if any(x in board for x in ['U', 'M']):
            # Invalid value or a mine was found on the board, end the game
            break
        if any(x in board for x in ['7', '8']):
            # Rare number encountered, save a screenshot
            take_unicorn_screenshot(category="unicorn_number", board_origo=board_origo, debug=debug)

        # Get all numbers 1-8 that are present on the board
        square_numbers = get_square_numbers_from_board(board)

        # Mark all detected mines with flags
        while True:
            # Mark one flag at a time, probabilities must be updated for each flag
            calc_base_probabilities(board, probabilities)
            set_square_number_probabilities(square_numbers, probabilities, board)
            if not mark_mine_with_flag(probabilities, board, board_origo=board_origo, debug=debug):
                # No more flags found
                break
            flag_count += 1

        if flag_count == TOTAL_NUM_MINES:
            # All mines were found
            while '-' in board:
                # Open remaining unopened square
                mine_idx = board.index('-')
                click_square(row=mine_idx // COLS, col=mine_idx % COLS, button='left', board_origo=board_origo)
                if game_won_displayed():
                    # High score table is visible, game has ended
                    break
                # Update board state after click
                im = take_board_screenshot(board_origo)
                board = read_board_state(im)
                if 'U' in board:
                    break
            # Game won, quit minesweeper
            quit()

        if debug:
            show_probability_matrix(probabilities)
            print_result(board)


def reset_game():
    """ If game ended and popup 'Reset the Game?' is displayed, click 'Yes' and reset game. """
    reset_button_location = pyautogui.locateOnScreen('img/reset_game_locator.png', confidence=0.9)
    if reset_button_location:
        locator_point = pyautogui.center(reset_button_location)
        pyautogui.click(locator_point.x, locator_point.y)


def setup():
    """ Game setup. Locate 'New game' button in order to calculate the origo of the game board. """
    new_game_btn_location = pyautogui.locateOnScreen('img/new_game_locator.png', confidence=0.9)
    if new_game_btn_location is None:
        print("Couldn't locate 'New' button. Make sure it's visible on the screen.")
        quit()
    locator_point = pyautogui.center(new_game_btn_location)
    pyautogui.click(locator_point.x, locator_point.y)
    board_origo = (new_game_btn_location[0] + BOARD_LEFT_TOP[0], new_game_btn_location[1] + BOARD_LEFT_TOP[1])
    return board_origo


def click_square(row, col, button, board_origo):
    """ Make a mouseclick on a square on the board with left or right button. """
    if not (0 <= row <= ROWS and 0 <= col <= COLS):
        return
    col_coord = board_origo[0] + SQUARE_WIDTH / 2 + col * SQUARE_WIDTH
    row_coord = board_origo[1] + SQUARE_HEIGHT / 2 + row * SQUARE_HEIGHT
    pyautogui.click(x=col_coord, y=row_coord, button=button)


def take_board_screenshot(board_origo):
    """ Take a screenshot of the game board, return the image. """
    with mss.mss() as sct:
        monitor = {'top': board_origo[1], 'left': board_origo[0], 'width': WIDTH, 'height': HEIGHT}
        sct_img = sct.grab(monitor)
        im = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    return im


def take_unicorn_screenshot(category, board_origo, debug):
    """ If a 7 or 8 occur on the board, or all mines are flagged - take a screenshot.
     Numbers 7 and 8 are rare, as is a round where all mines are flagged. """
    if debug:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        file_ending = f"{category}__{timestamp}"
        pyautogui.screenshot(f"screenshots/screenshot_{file_ending}.png",
                             region=(board_origo[0], board_origo[1], WIDTH, HEIGHT))


def get_square_numbers_from_board(board):
    """ Return all square numbers on the board (1-8); value and position on the board. """
    square_numbers = {}
    for idx in range(len(board)):
        if board[idx] in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            # Convert number representation to number
            square_numbers[idx] = int(board[idx])  # {board index: integer square number}
    return square_numbers


def calc_base_probabilities(board, probabilities):
    """ Calculate the base probability by dividing the remaining number of mines (unflagged mines)
        with the number of unopened squares. """
    probabilities.clear()
    unopened_squares = board.count('-')
    num_mines_left = TOTAL_NUM_MINES - board.count('F')

    for row in range(ROWS):
        for col in range(COLS):
            idx = col + row * COLS
            if board[idx] == '-':
                prob = round(num_mines_left / unopened_squares, 2)
            elif board[idx] == 'F':
                prob = "-mm-"
            else:
                prob = "-xx-"    # opened squares and square numbers (1-8)
            probabilities.append(prob)


def set_square_number_probabilities(square_numbers, probabilities, board):
    """
    Set the square numbers' neighbour probabilities based upon how many mines and
    unopened squares they have in the neighbourhood.
    """
    for square_num_idx in square_numbers:  # {value index: number value}
        curr_col, curr_row = square_num_idx % COLS, square_num_idx // COLS
        neighbour_positions = [
            (curr_col - 1, curr_row - 1), (curr_col, curr_row - 1), (curr_col + 1, curr_row - 1),
            (curr_col - 1, curr_row),     (curr_col, curr_row),     (curr_col + 1, curr_row),
            (curr_col - 1, curr_row + 1), (curr_col, curr_row + 1), (curr_col + 1, curr_row + 1)
        ]

        neighbours_idx = []
        for col, row in neighbour_positions:
            if 0 <= row < ROWS and 0 <= col < COLS:
                idx = col + row * COLS
                neighbours_idx.append(idx)  # Add index of neighbours_idx

        neighbour_probs = calc_square_number_probabilities(square_numbers[square_num_idx], neighbours_idx, board)

        for idx, neigh_idx in enumerate(neighbours_idx):
            base_prob = probabilities[neigh_idx]
            neighbour_prob = neighbour_probs[idx]
            if base_prob in ["-mm-", "-xx-"] or base_prob == 0.0:
                continue
            if neighbour_prob > base_prob or neighbour_prob == 0.0:
                probabilities[neigh_idx] = neighbour_prob


def calc_square_number_probabilities(square_number, neighbours_idx, board_values):
    """
    Each square number (1-8) has a number of neighbours (surrounding squares). A '1' has one and only one mine
    as a neighbour, a '2' has two and only two mines in the neighbourhood. Calculate the square numbers' neighbour
    probabilities based upon how many mines and unopened squares they have in the neighbourhood.
    """
    num_mines, num_unopened_squares = 0, 0
    for idx in neighbours_idx:
        if board_values[idx] == 'F':
            num_mines += 1
        elif board_values[idx] == '-':
            num_unopened_squares += 1
    prob = 0
    neighbour_probabilities = []
    if num_unopened_squares > 0:
        prob = max(0.0, (square_number - num_mines) / num_unopened_squares)

    for neighbour_idx in neighbours_idx:
        if board_values[neighbour_idx] == '-':
            neighbour_probabilities.append(round(prob, 2))
        else:
            neighbour_probabilities.append(None)
    return neighbour_probabilities


def mark_mine_with_flag(probabilities, board, board_origo, debug=False):
    """ Mark mines on the board by right clicking on them with the mouse, add mine to board values. """
    mine_indices = [i for i, prob in enumerate(probabilities) if prob == 1.00]
    for mine_idx in mine_indices:
        if board[mine_idx] == 'F':
            continue
        row = mine_idx // COLS
        col = mine_idx % COLS
        click_square(row=row, col=col, button='right', board_origo=board_origo)
        probabilities[col + row * COLS] = "-mm-"  # Mark mine in probabilities
        board[mine_idx] = 'F'                     # Mark mine in board
        if board.count('F') == TOTAL_NUM_MINES:
            take_unicorn_screenshot(category="all_mines_flagged", board_origo=board_origo, debug=debug)
        return True
    return False


def game_won_displayed():
    """ If high score is displayed - game is won! """
    high_score_location = pyautogui.locateOnScreen('img/win_locator.png', confidence=0.9)
    if high_score_location:
        print("Game won! :)")
        return True
    return False


def show_probability_matrix(probabilities):
    """ Print out probability matrix in the terminal. """
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


def print_result(board_values):
    """ Print out game statistics in the terminal. """
    print("\n----  Result  ----")
    print("Mines left:", TOTAL_NUM_MINES - board_values.count('F'))
    print("Squares left:", board_values.count('-'))
