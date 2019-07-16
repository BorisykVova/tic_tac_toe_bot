from math import inf

from game_models import GameField

MAX_DEPTH = inf


def minimax(game_field: GameField, player: int, my_move: bool, depth: int, alpha, beta) -> int:
    if depth > MAX_DEPTH:
        return 0
    winner = game_field.check_winner()
    if winner != 0:
        return winner

    score = alpha if my_move else beta
    move_row, move_col = -1, -1
    board = game_field.data

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == 0:
                game_field.make_move(i, j, player, 0)

                if my_move:
                    current_score = minimax(game_field, -player, not my_move, depth + 1, score, beta)
                    game_field.make_move(i, j, 0, 0)
                    if current_score > score:
                        score = current_score
                        move_row, move_col = i, j
                        if score >= beta:
                            game_field.best_row = move_row
                            game_field.best_col = move_col
                            return score
                else:
                    current_score = minimax(game_field, -player, not my_move, depth + 1, alpha, score)
                    game_field.make_move(i, j, 0, 0)
                    if current_score < score:
                        score = current_score
                        move_row, move_col = i, j
                        if score <= alpha:
                            game_field.best_row = move_row
                            game_field.best_col = move_col
                            return score
    if move_row == - 1:
        return 0
    game_field.best_row = move_row
    game_field.best_col = move_col
    return score
