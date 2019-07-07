from math import inf

from border_worker import Board


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
        self.board = Board.init_board(self.board_size)
        self.total_moves = 0
