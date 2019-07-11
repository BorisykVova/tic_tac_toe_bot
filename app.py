from math import inf
import random

import telebot

from game_session import UserSession
from border_worker import Board
from get_score import ret, minimax

TOKEN = '637684041:AAEpncPlFsmLlG3tyHbbjDobPtBqUB8wiDc'
bot = telebot.TeleBot(TOKEN)


count = 0
user_session = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'This is a tic-tac-toe game. \n To start playing as X, enter the command: \n'
                                      '/start_x. \n To start playing as O, enter the command: \n/start_o. \n In order'
                                      ' to make a move you need to enter the coordinates of the desired cell through'
                                      ' a space')


@bot.message_handler(commands=['start_x'])
def start_x(message):
    user_session[message.chat.id] = UserSession('X')
    session: UserSession = user_session[message.chat.id]
    board = session.board
    bot.send_message(message.chat.id, Board.str_board(board))


@bot.message_handler(commands=['start_o'])
def start_o(message):
    user_session[message.chat.id] = UserSession('O')
    session: UserSession = user_session[message.chat.id]
    board = session.board
    bot.send_message(message.chat.id, Board.str_board(board))
    send_answer(message)


@bot.message_handler(func=lambda message: True)
def send_answer(message):

    if message.chat.id in user_session:
        session: UserSession = user_session[message.chat.id]
    else:
        return bot.send_message(message.chat.id, "GAME IS OVER")

    row, col = session.row, session.col
    board_size = session.board_size
    machine_player = session.machine_player
    current_player = session.current_player
    my_move = session.my_move
    total_moves = session.total_moves
    board = session.board

    if current_player == machine_player:
        if total_moves <= 1:
            row, col = random.randint(0, board_size - 1), random.randint(0, board_size - 1)
        else:
            score = minimax(board, current_player, my_move, 0, -inf, inf)
            if score != -inf:
                row, col = ret()
    else:
        try:
            row, col = map(lambda x: int(x) - 1, str(message.text).split())
        except ValueError:
            bot.send_message(message.chat.id, 'You need to enter the coordinates of the desired cell through a space')

    if 0 <= row < board_size and 0 <= col < board_size:
        if board[row][col] == 0:
            board[row][col] = current_player
            current_player *= -1
            total_moves += 1

    session.board = board
    session.current_player = current_player
    session.total_moves = total_moves

    bot.send_message(message.chat.id, Board.str_board(board))

    winner = Board.check_winner(board)
    if winner:
        del user_session[message.chat.id]
        return bot.send_message(message.chat.id, f"WIN FOR {'O' if winner is 1 else 'X'} !!!!")

    if total_moves == board_size ** 2:
        del user_session[message.chat.id]
        return bot.send_message(message.chat.id, "GAME IS OVER")

    if current_player == machine_player:
        send_answer(message)


bot.polling()
