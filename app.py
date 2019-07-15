import typing as typ
from math import inf
import random

import telebot
from telebot.apihelper import ApiException
from telebot.types import Message, CallbackQuery as Call
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from game_session import UserSession
from border_worker import Board
from get_score import ret, minimax

TOKEN = '637684041:AAEpncPlFsmLlG3tyHbbjDobPtBqUB8wiDc'
bot = telebot.TeleBot(TOKEN)


count = 0
user_session = {}


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    bot.send_message(message.chat.id, 'None')


@bot.message_handler(commands=['start'])
def new_game(message: Message = None, user_id=None):
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton('New game', callback_data='start')
    markup.add(button)
    chat_id = message.chat.id if message else user_id
    bot.send_message(chat_id, 'Chose:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'start')
def chose_side(call: Call):
    chat_id = call.from_user.id
    markup = InlineKeyboardMarkup(2)
    markup.row(InlineKeyboardButton('❌', callback_data='X'), InlineKeyboardButton('⭕️', callback_data='O'))
    bot.send_message(chat_id, 'Chose your side:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['X', 'O'])
def side_callback(call: Call):
    chat_id = call.from_user.id
    data = call.data
    user_session[chat_id] = UserSession(data)
    if data is 'O':
        send_answer(chat_id)
    else:
        session: UserSession = user_session[chat_id]
        board = session.board
        bot.send_message(chat_id, 'Game: ', reply_markup=Board.button_board(board))


@bot.callback_query_handler(func=lambda call: True)
def callback(call: Call):
    chat_id = call.from_user.id
    message_id = call.message.message_id
    move = [*map(int, str(call.data).split(' '))]
    if chat_id in user_session:
        send_answer(chat_id, message_id, move)


def send_answer(user_id: int = None, message_id: int = None, move: typ.List[int] = None):

    session: UserSession = user_session[user_id]

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
        row, col = move
    if 0 <= row < board_size and 0 <= col < board_size:
        if board[row][col] == 0:
            board[row][col] = current_player
            current_player *= -1
            total_moves += 1

    session.board = board
    session.current_player = current_player
    session.total_moves = total_moves

    if message_id:
        try:
            bot.edit_message_reply_markup(user_id, message_id, reply_markup=Board.button_board(board))
        except ApiException:
            pass
    else:
        bot.send_message(user_id, 'Game: ', reply_markup=Board.button_board(board))

    winner = Board.check_winner(board)
    if winner:
        del user_session[user_id]
        text = 'You lose' if winner == machine_player else 'You won'
        bot.send_message(user_id, text)
        return new_game(user_id=user_id)

    if total_moves == board_size ** 2:
        del user_session[user_id]
        return bot.send_message(user_id, "GAME IS OVER")

    if current_player == machine_player:
        send_answer(user_id, message_id)


bot.polling()
