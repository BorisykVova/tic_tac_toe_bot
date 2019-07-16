import typing as typ
from math import inf
import random

import telebot
from telebot.apihelper import ApiException
from telebot.types import Message, CallbackQuery as Call, User
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from game_models import UserSession, GameField
from get_score import minimax

TOKEN = '843352714:AAG-24gS3rxGOAe4w0uL7EOP_oPdVilhN3k'
bot = telebot.TeleBot(TOKEN)


count = 0
user_session = {}


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    bot.send_message(message.chat.id, 'None')


@bot.message_handler(commands=['start'])
def new_game(message: Message = None, user_id=None):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton('New game', callback_data='start'))
    chat_id = message.chat.id if message else user_id
    bot.send_message(chat_id, 'Chose:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'start')
def chose_side(call: Call):
    chat_id = call.from_user.id
    message_id = call.message.message_id
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton('❌', callback_data='X'),
               InlineKeyboardButton('⭕️', callback_data='O'))
    bot.delete_message(chat_id, message_id)
    bot.send_message(chat_id, 'Chose your side:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['X', 'O'])
def side_callback(call: Call):
    chat_id = call.from_user.id
    message_id = call.message.message_id
    data = call.data
    user_session[chat_id] = UserSession(data)
    bot.delete_message(chat_id, message_id)

    if data is 'O':
        send_answer(chat_id, chat_id, first_message=True)
    else:
        session: UserSession = user_session[chat_id]
        game_field = session.game_field
        bot.send_message(chat_id, f'You are playing as {game_field.board_element(-1)}',
                         reply_markup=game_field.button_board())


@bot.callback_query_handler(func=lambda call: True)
def callback(call: Call):
    chat_id = call.from_user.id
    message_id = call.message.message_id
    move = [*map(int, str(call.data).split(' '))]
    if chat_id in user_session:
        send_answer(chat_id, message_id, move)


def end_move(game_field: GameField, chat_id: int, message_id: int, machine_player: int, current_player: int):
    winner = game_field.check_winner()
    if winner:
        del user_session[chat_id]
        text = 'You lose' if winner == machine_player else 'You won'
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, f'{game_field.str_board()}{text}')
        return new_game(user_id=chat_id)

    if game_field.total_moves == game_field.size() ** 2:
        del user_session[chat_id]
        text = 'Game over'
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, f'{game_field.str_board()}{text}')
        return new_game(user_id=chat_id)

    if current_player == machine_player:
        send_answer(chat_id, message_id)


def send_answer(chat_id: int, message_id: int, move: typ.List[int] = None, first_message=False):

    session: UserSession = user_session[chat_id]
    machine_player = session.machine_player
    current_player = session.current_player
    row, col = session.row, session.col
    my_move = session.my_move

    game_field: GameField = session.game_field
    board_size = game_field.size()
    total_moves = game_field.total_moves
    board = game_field.data

    if current_player == machine_player:
        if total_moves <= 1:
            row, col = random.randint(0, game_field.size() - 1), random.randint(0, game_field.size() - 1)
        else:
            score = minimax(game_field, current_player, my_move, 0, -inf, inf)
            if score != -inf:
                row, col = game_field.best_row, game_field.best_col
    else:
        try:
            row, col = move
        except TypeError:
            return

    if 0 <= row < board_size and 0 <= col < board_size:
        if board[row][col] == 0:
            game_field.make_move(row, col, current_player)
            current_player *= -1

    session.game_field = game_field
    session.current_player = current_player

    if first_message:
        bot.send_message(chat_id, f'You are playing as {game_field.board_element(1)}',
                         reply_markup=game_field.button_board())
    else:
        try:
            bot.edit_message_reply_markup(chat_id, message_id, reply_markup=game_field.button_board())
        except ApiException:
            pass

    end_move(game_field, chat_id, message_id, machine_player, current_player)


bot.polling()
