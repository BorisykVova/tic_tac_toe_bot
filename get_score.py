from math import inf
import typing as typ

from border_worker import Board

MAX_DEPTH = inf
best_row = -1
best_col = -1


def minimax(board: typ.List[typ.List[int]], player: int, my_move: bool, depth: int, alpha, beta) -> int:
    if depth > MAX_DEPTH:
        return 0
    winner = Board.check_winner(board)
    if winner != 0:
        return winner

    global best_col, best_row
    score = alpha if my_move else beta
    move_row, move_col = -1, -1

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == 0:
                board[i][j] = player

                if my_move:
                    current_score = minimax(board, -player, not my_move, depth + 1, score, beta)
                    board[i][j] = 0
                    if current_score > score:
                        score = current_score
                        move_row, move_col = i, j
                        if score >= beta:
                            best_row = move_row
                            best_col = move_col
                            return score
                else:
                    current_score = minimax(board, -player, not my_move, depth + 1, alpha, score)
                    board[i][j] = 0
                    if current_score < score:
                        score = current_score
                        move_row, move_col = i, j
                        if score <= alpha:
                            best_row = move_row
                            best_col = move_col
                            return score
    if move_row == - 1:
        return 0
    best_row = move_row
    best_col = move_col
    return score


def ret() -> typ.Tuple[int, int]:
    return best_row, best_col
