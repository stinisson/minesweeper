import time
from kmines_hard import run_game


def main(debug=False):
    for i in range(1):
        run_game(debug)
        time.sleep(3)


if __name__ == '__main__':
    main(debug=False)
