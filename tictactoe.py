import random


def blank_board():
    board = [[" " for _ in range(3)] for _ in range(3)]
    return board


def is_filled(board):
    for row in board:
        if " " in row:
            return False
    return True


def check_end(board):
    # rows
    for row in board:
        if "".join(row) == "XXX":
            return True, "X"
        if "".join(row) == "OOO":
            return True, "O"
    # columns
    for col in range(3):
        first = board[0][col]
        if first not in ['X', 'O']:
            continue
        if first == board[1][col] and first == board[2][col]:
            return True, first
    # diagonals
    first = board[0][0]
    if first in ['X', 'O']:
        done = True
        for i in range(1, 3):
            if board[i][i] != first:
                done = False
                break
        if done:
            return True, first
    first = board[2][0]
    if first in ['X', 'O']:
        done = True
        for i in range(1, 3):
            if board[2 - i][i] != first:
                done = False
                break
        if done:
            return True, first
    if is_filled(board):
        return True, "Draw"
    return False, ""


def add_element(board, place, el):
    cells = {1: (0, 0), 2: (0, 1), 3: (0, 2),
             4: (1, 0), 5: (1, 1), 6: (1, 2),
             7: (2, 0), 8: (2, 1), 9: (2, 2)}
    row, col = cells[place]
    # space is already filled
    if board[row][col] != " ":
        return False, board
    board[row][col] = el
    return True, board


def get_result(res):
    if len(res) == 1:
        return res + " wins"
    return res


b = blank_board()
letters = {True: "X", False: "O"}
X = True
while not is_filled(b):
    success, b = add_element(b, random.randint(1, 9), letters[X])
    if success:
        X = not X
        end, result = check_end(b)
        if end:
            print(get_result(result))
            break
for r in b:
    print(r)
