import sys
import fsm
import time
import telegram

from io import BytesIO

from flask import Flask, request, send_file

from fsm import TocMachine

from telegram.ext import Dispatcher
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

API_TOKEN = '375506753:AAGeRZuDa89KhOrWWopmBWk6RE9IS-3nG4g'
WEBHOOK_URL = 'https://27b98064.ngrok.io/hook'

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)

dispatcher = Dispatcher(bot, None, workers=0)
first = 0
ooxx_text = 'Error'
ooxx_id = 0

machine = TocMachine(
    states=[
        'user',
        'bmi',
        'bmi_height',
        'bmi_show',
        'bmi_error',
        'photo',
        'photo_beauty',
        'photo_beauty_candice',
        'photo_beauty_deer',
        'photo_hell',
        'leave_photo',
        'state3',
        'ooxx',
        'state4',
        'state5',
        'hint'
    ],
    transitions=[
        {
            'trigger': 'advance',
            'source': [
                'user'
            ],
            'dest': 'bmi',
            'conditions': 'is_going_to_bmi'
        },
        {
            'trigger': 'advance',
            'source': [
                'bmi',
                'bmi_error'
            ],
            'dest': 'bmi_height',
            'conditions': 'is_going_to_bmi_height'
        },
        {
            'trigger': 'advance',
            'source': [
                'bmi_height',
                'bmi_error'
            ],
            'dest': 'bmi_show',
            'conditions': 'is_going_to_bmi_show'
        },
        {
            'trigger': 'advance',
            'source': [
                'bmi',
                'bmi_height',
                'bmi_error'
            ],
            'dest': 'bmi_error',
            'conditions': 'is_going_to_bmi_error'
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'photo',
            'conditions': 'is_going_to_photo'
        },
        {
            'trigger': 'advance',
            'source': 'photo',
            'dest': 'photo_beauty',
            'conditions': 'is_going_to_photo_beauty'
        },
        {
            'trigger': 'advance',
            'source': 'photo',
            'dest': 'photo_hell',
            'conditions': 'is_going_to_photo_hell'
        },
        {
            'trigger': 'advance',
            'source': 'photo_beauty',
            'dest': 'photo_beauty_candice',
            'conditions': 'is_going_to_photo_beauty_candice'
        },
        {
            'trigger': 'advance',
            'source': 'photo_beauty',
            'dest': 'photo_beauty_deer',
            'conditions': 'is_going_to_photo_beauty_deer'
        },
        {
            'trigger': 'advance',
            'source': [
                'photo',
                'photo_beauty'
            ],
            'dest': 'leave_photo',
            'conditions': 'is_going_to_leave_photo'
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'state3',
            'conditions': 'is_going_to_state3'
        },
        {
            'trigger': 'advance',
            'source': [
                'user',
                'ooxx',
                'state4'
            ],
            'dest': 'ooxx',
            'conditions': 'is_going_to_ooxx'
        },
        {
            'trigger': 'advance',
            'source': 'ooxx',
            'dest': 'state4',
            'conditions': 'is_going_to_state4'
        },
        {
            'trigger': 'advance',
            'source': [
                'state4',
                'ooxx'
            ],
            'dest': 'state5',
            'conditions': 'is_going_to_state5'
        },
        {
            'trigger': 'advance',
            'source': [
                'user'
            ],
            'dest': 'hint',
            'conditions': 'is_going_to_hint'
        },
        {
            'trigger': 'go_back',
            'source': [
                'bmi_show',
                'leave_photo',
                'photo_beauty_candice',
                'photo_beauty_deer',
                'photo_hell',
                'state3',
                'state5',
                'hint'
            ],
            'dest': 'user'
        }
    ],
    initial='user',
    auto_transitions=False,
    show_conditions=True,
)


def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)

    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))

def edit(bot ,query ,reply_markup ,end):
    global ooxx_text
    print(query.message.message_id)
    if end == 1:
        bot.edit_message_text(text = ooxx_text,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
    else :
        bot.edit_message_text(text = ooxx_text,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id
                                ,reply_markup =reply_markup )
def get_keyboard() :
    keyboard = []  
    for x in range (0, 3):                               
        new = []                  
        for y in range (0, 3): 
            foo = InlineKeyboardButton("%s"%fsm.puzzle[x][y], callback_data="%s"%str(x*3+y))  
            new.append(foo)  
        keyboard.append(new)  
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def button(bot, update):
    global ooxx_text

    if fsm.OX == 1 :

        query = update.callback_query
        fsm.id_message = query.message.message_id
        v = int(query.data)
        j = int(v%3)
        i = int((v-j)/3)
        
        op = fsm.ooxx_push(i ,j ,1)
     
        reply_markup = get_keyboard()
    
        if op == 3 :
            time.sleep(0.5)
            ooxx_text = "Tie"
            fsm.ooxx_end()
            edit(bot ,query ,reply_markup ,1) 
            #update = update.callback_query

        elif op == 2 :
            edit(bot ,query ,reply_markup ,0) 

            time.sleep(0.5)

            ooxx_text = "You win"
            fsm.ooxx_end()
            edit(bot ,query ,reply_markup ,1)
            #update = update.callback_query

        elif op == 1 :
            ooxx_text = "Bot's  turn :\n\nType exit to leave the game"
            edit(bot ,query ,reply_markup ,0)

            do = fsm.ooxx_AI()

            if do == 2 :
                reply_markup = get_keyboard()
                edit(bot ,query ,reply_markup ,0)
                
                time.sleep(0.5)
                ooxx_text = " You lose "
                fsm.ooxx_end()
                edit(bot ,query ,reply_markup ,1)
                #update = update.callback_query

            elif do == 1 :
                reply_markup = get_keyboard()
                
                time.sleep(0.5)
                ooxx_text = "Your   turn :\n\nType exit to leave the game"
                edit(bot ,query ,reply_markup ,0)

        elif op == 0 :

            ooxx_text =     "The grid has been filled !\nPlease pick a empty grid !\n\nType exit to leave the game"
            edit(bot ,query ,reply_markup ,0)

            time.sleep(0.5)
    #bot.message.delete_message(chat_id=query.message.chat_id,
    #                    message_id=query.message.message_id)
    #query.message.reply_text("press %d %d" % (x ,y))

    
dispatcher.add_handler(CallbackQueryHandler(button))

@app.route('/hook', methods=['POST'])
def webhook_handler():
    global first
    global bot

    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    
    if first == 0 :
        fsm.id_chat = update.message.chat_id    
        first = 1

    if first == 1 :
        machine.advance(update)
    return 'ok'

@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')


if __name__ == "__main__":
    _set_webhook()
    app.run()
    



