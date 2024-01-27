import telebot
import requests
from main import send_message, hit, stand, GameData

telegram_token_bot = os.environ['TELEGRAM_BOT_TOKEN']
bot = telebot.TeleBot(telegram_token_bot)
game_data = GameData()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Добро пожаловать в игру блэкджек!")


@bot.message_handler(commands=['newgame'])
def start_new_game(message):
    global game_data
    game_data = GameData()
    game_data.deck_id =         requests.get('https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1').json()['deck_id']

    send_message(message, "Новая игра началась! Используйте /hit, чтобы взять карту")


@bot.message_handler(commands=['hit', 'stand'])
def handle_commands(message):
    global game_data
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_data = bot.get_chat_member(chat_id, user_id)
    if user_data.status not in ["member", "administrator", "creator"]:
        send_message(message, "Вы не можете использовать эти команды.")
        return
    command = message.text.lower()
    if command == '/hit':
        hit(game_data.deck_id, game_data.player_hand, message)
    elif command == '/stand':
        stand(game_data.deck_id, game_data.player_hand, game_data.dealer_hand, message)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.message:
        pass


bot.polling()
