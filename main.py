import os
import requests
import telebot
from telebot import types

telegram_token_bot = os.environ['TELEGRAM_BOT_TOKEN']
bot = telebot.TeleBot(telegram_token_bot)

class GameData:
    def __init__(self):
        self.deck_id = ''
        self.player_hand = []
        self.dealer_hand = []
        self.game_started = False

game_data = GameData()

def send_message(message, text, reply_markup=None):
    bot.send_message(message.chat.id, text, reply_markup=reply_markup)

def send_card_image(message, image_url):
    bot.send_photo(message.chat.id, image_url)

def create_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('/hit'), types.KeyboardButton('/stand'))
    return keyboard

def card_value_to_int(card_value):
    if card_value.lower() in ['king', 'queen', 'jack']:
        return 10
    elif card_value.lower() == 'ace':
        return 11
    else:
        return int(card_value)

def deal_initial_cards(deck_id):
    player_hand = [draw_card(deck_id), draw_card(deck_id)]
    dealer_hand = [draw_card(deck_id), draw_card(deck_id)]
    return player_hand, dealer_hand

def draw_card(deck_id):
    response = requests.get(f'https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count=1')
    card_info = response.json()['cards'][0]
    image_url = card_info['image']
    return card_info, image_url

def hit(deck_id, player_hand, message):
    global game_data
    card_info, image_url = draw_card(deck_id)
    player_hand.append(card_info)
    player_score = calculate_score(player_hand)
    bot.reply_to(message, f"Вы взяли карту {card_info['value']}. Ваш счет: {player_score}.")
    send_card_image(message, image_url)

    if player_score > 21:
        bot.reply_to(message, "Вы проиграли!")
        end_game(message, False)
    else:
        send_message(message, "Ваш ход:", create_keyboard())

def stand(deck_id, player_hand, dealer_hand, message):
    global game_data
    dealer_images = []

    for card in dealer_hand:
        dealer_images.append(card['image'])
        send_card_image(message, card['image'])

    while calculate_score(dealer_hand) < 17:
        card_info, image_url = draw_card(deck_id)
        dealer_hand.append(card_info)
        dealer_images.append(image_url)
        send_card_image(message, image_url)

    dealer_score = calculate_score(dealer_hand)
    player_score = calculate_score(player_hand)

    if dealer_score > 21 or player_score > dealer_score:
        send_message(message, "Вы выиграли!")
    elif dealer_score > player_score:
        send_message(message, "Вы проиграли!")
    else:
        send_message(message, "Ничья!")

    end_game(message, True)

def calculate_score(hand):
    values = [card_value_to_int(card['value']) for card in hand]
    score = sum(values)
    ace_count = sum(1 for card in hand if card['value'] == 'ACE')

    while score > 21 and ace_count > 0:
        score -= 10
        ace_count -= 1

    return score

def end_game(message, show_balance=True):
    global game_data
    game_data.game_started = False
    if show_balance:
        send_message(message, "Игра завершена.Используйте /newgame для начала новой игры.")
    else:
        send_message(message, "Игра завершена. Используйте /newgame, чтобы начать новую игру.")
