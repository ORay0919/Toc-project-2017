import time
import __main__

from transitions.extensions import GraphMachine
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import  CommandHandler, CallbackQueryHandler
 
puzzle  = [['_' for x in range(3)] for y in range(3)] 
OX = 0
id_chat = 0
id_message = 0

def ooxx_end() :
    global OX
    OX = 2

def ooxx_check(who):

    if who == 0:
        sign = 'X'
    elif who == 1:
        sign = 'O'        

    for i in range(3):
        row = puzzle[i].count(sign)
        if row == 3:
            return who
        col = [puzzle[k][i]for k in range(3)].count(sign)
        if col == 3:
            return who

    cross = [puzzle[k][k]for k in range(3)].count(sign)
    if cross == 3 :
        return who

    cross = [puzzle[k][2-k]for k in range(3)].count(sign)
    if cross == 3 :
        return who
    
    return -1

def ooxx_push(x ,y ,who):
    global puzzle

    if who == 0:
        sign = 'X'
    elif who == 1:
        sign = 'O' 

    if puzzle[x][y] != '_':
        flag = 0
    else :
        puzzle[x][y] = sign
        flag = 1
    
    check = ooxx_check(who)

    if check != -1 :
        flag = 2
    else :
        tie = 0
        for i in range(3):
            tie += puzzle[i].count('_')
        if tie == 0 :
            return 3

    return flag

def calcPoint(line):
    point = 0
    if line.count('X') == 2:
        point += 1000
    if line.count('O') == 2:
        point += 900
    if line.count('X') == 1 and line.count('O') == 0:
        point += 100
    if line.count('X') == 0 and line.count('O') == 1:
        point += 90
    if line.count('_') == 3:
        point += 10
    return point

def ooxx_AI():
    global puzzle

    max_point = -1
    point = [[0 for x in range(3)] for y in range(3)] 

    for i in range(3):
        for j in range(3):
            if puzzle[i][j] != '_':
                point[i][j] = -1
                continue
            # row
            point[i][j] += calcPoint(puzzle[i])
            # col
            line = [puzzle[k][j] for k in range(3)]
            point[i][j] += calcPoint(line)
            # left-top to right-bottom
            if i == j:
                line = [puzzle[k][k] for k in range(3)]
                point[i][j] += calcPoint(line)
            # right-top to left-bottom
            if i + j == 2:
                line = [puzzle[k][2 - k] for k in range(3)]
                point[i][j] += calcPoint(line)
            # center
            if i == 1:
                point[i][j] += 1
            if j == 1:
                point[i][j] += 1
            if point[i][j] > max_point:
                max_point = point[i][j]
                position = (i, j)
    
    return ooxx_push(position[0] ,position[1] ,0)

#######################################################################

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )


#######################################################################
    def is_going_to_state1(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text.lower() == '1'

    def is_going_to_photo(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text.lower() == 'photo'

    def is_going_to_send_photo(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text.lower() == '1'

    def is_going_to_leave_photo(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text.lower() == '3'

    def is_going_to_state3(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text.lower() == 's3'

    def is_going_to_ooxx(self, update):
        global OX
        
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False

        if OX == 0 :
            return text.lower() == "ooxx"
        elif OX == 2 :
            return text.lower() == "y"

    def is_going_to_state4(self, update):
        global OX

        if OX == 2 :
            return True

        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False

        return False
    
    def is_going_to_state5(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text.lower() == "n"

#######################################################################
    def on_enter_state1(self, update):
        update.message.reply_text("I'm entering state1")
        self.go_back(update)

    def on_exit_state1(self, update):
        print('Leaving state1')


#######################################################################
    def on_enter_photo(self, update):
        global id_chat
        
        update.message.reply_text("Which kind of photo do you want?\nPlease type the number :\n1 : Beauty\n2 : 長輩圖\n3 : Leave photo")
        #self.go_back(update)

    def on_exit_photo(self, update):
        print('Leaving photo')
#######################################################################
    def on_enter_send_photo(self, update):
        global id_chat
        __main__.bot.send_photo(chat_id= id_chat ,photo=open('./pic/1.jpg', 'rb'))
        #update.message.reply_text("I'm entering state1")
        self.go_back(update)

    def on_exit_photo(self, update):
        print('Leaving send photo')
#######################################################################
    def on_enter_leave_photo(self, update):
        update.message.reply_text("Leave photo")
        self.go_back(update)

    def on_leave_photo(self, update):
        print('Leaving photo')

#######################################################################
    def on_enter_state3(self, update):
        update.message.reply_text("I'm entering state3")
        self.go_back(update)

    def on_exit_state3(self, update):
        print('Leaving state3')


#######################################################################
    def on_enter_ooxx(self, update):
        global puzzle
        global OX 
        
        if OX != 1:
            OX = 1
            puzzle  = [['_' for x in range(3)] for y in range(3)] 
            puzzle =[['X','O','O'],['O','X','X'],['X','_','O']]
            keyboard = []
            
            for x in range (0, 3):                     
                new = []                  
                for y in range (0, 3):  
                    foo = InlineKeyboardButton("%s"%puzzle[x][y], callback_data="%s"%str(x*3+y))  
                    new.append(foo)  
                keyboard.append(new)  
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            __main__.bot.send_message(chat_id= id_chat,text='You go first:', reply_markup=reply_markup)
            #self.go_back(update)

    def on_exit_ooxx(self, update):
        print('Leaving ooxx')

#######################################################################
    def on_enter_state4(self, update):
        #update.message.reply_text("I'm entering state4")
        global id_chat
        __main__.bot.send_message(chat_id= id_chat,text='Do you want to play another game?\nY/N')
        print('state4')
        #self.go_back(update)

    def on_exit_state4(self, update):
        print('Leaving state4')

#######################################################################
    def on_enter_state5(self, update):
        global OX
        OX = 0

        update.message.reply_text("I'm entering state5")
        self.go_back(update)

    def on_exit_state5(self, update):
        print('Leaving state5')

#######################################################################

