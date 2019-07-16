from math import inf

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


class GameField:
    def __init__(self, board_size: int) -> None:
        self.data = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.total_moves = 0
        self.best_row = -1
        self.best_col = -1

    def size(self):
        return len(self.data)

    def make_move(self, row: int, col: int, value: int, moves: int = 1):
        self.data[row][col] = value
        self.total_moves += moves

    def button_board(self) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        board = self.data
        for i, row in enumerate(board):
            button_list = [InlineKeyboardButton(self.board_element(cell), callback_data=f'{i} {j}')
                           for j, cell in enumerate(row)]
            keyboard.row(*button_list)
        return keyboard

    def str_board(self) -> str:
        board = self.data
        board = [[self.board_element(cell) for cell in row] for row in board]
        str_board = ''
        for row in board:
            str_board += ''.join(row) + '\n'
        return str_board

    @classmethod
    def board_element(cls, cell: int) -> str:
        if cell == 0:
            return '⬜️'
        if cell == -1:
            return '❌'
        if cell == 1:
            return '⭕️'

    def check_winner(self) -> int:
        board = self.data
        board_size = len(board)

        if board[0][0] and all(el == board[0][0] for el in [board[i][i] for i in range(board_size)]):
            return board[0][0]
        if board[-1][0] and all(el == board[-1][0] for el in [board[i][-1 - i] for i in range(board_size)]):
            return board[board_size - 1][0]

        for row in board:
            if row[0] and all(el == row[0] for el in row):
                return row[0]
        for i in range(board_size):
            col = [board[j][i] for j in range(board_size)]
            if col[0] and all(el == col[0] for el in col):
                return col[0]
        return 0


class UserSession:
    def __init__(self, side: str):
        if side == 'O':
            self.machine_player = -1
            self.current_player = -1
            self.my_move = False
        else:
            self.machine_player = 1
            self.current_player = -1
            self.my_move = True
        self.board_size = 3
        self.max_depth = inf
        self.row = -1
        self.col = -1
        self.best_row = -1
        self.best_col = -1
        self.game_field = GameField(self.board_size)
