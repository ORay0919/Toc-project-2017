# -*- coding: utf8 -*-
import time
import __main__
import random
import requests, json
import datetime
from lxml import etree, html  
from transitions.extensions import GraphMachine
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import  CommandHandler, CallbackQueryHandler
 
puzzle  = [['_' for x in range(3)] for y in range(3)] 

bmi_state = 0
bmi_get_weight = 0.0
bmi_get_height = 0.0

root = 1
OX = 0
id_chat = 0
id_message = 0

hint_text     =  'Hint :\nThere are five commands so far.'
hint_text    +=  '\n(1) photo  : Get some photos'
hint_text    +=  '\n(2) ooxx    : Play tic-tac-toe with bot'
hint_text    +=  '\n(3) bmi      : Enter your weight and height ,you can know your bmi'
hint_text    +=  '\n(4) receipt : Get the last 3 times of receipt lottery numbers'
hint_text    +=  '\n(5) 3           : Don\'t doubt it. It\'s  3  but just for test only😂'

def get_next_month(y ,m) :
    r = []
    if m == 1 :
        y -= 1
        m  = 11
    else :
        m -= 2
    r.append(y)
    r.append(m)
    return r

def get_receipt_number(y ,m):
    
    text = str(y-1911)
    
    if m < 10 :
        text += '0'+str(m)
    else :
        text += str(m)
    result = requests.get("https://www.etax.nat.gov.tw/etw-main/web/ETW183W2_%s/"%text) 
    
    result.encoding = 'utf8'  
    root = etree.fromstring(result.content, etree.HTMLParser()) 
    i = []
    for row in root.xpath("//table[@class='table table-bordered']/tbody[position()>1]")  :
        column = row.xpath("./tr/td/span/text()")
        if len(column) > 0:
            for g in column:
                i.append(g)
    return i

def make_receipt_text(y ,m ,i) :
    
    text = "%s年"%str(y-1911)
    
    if m < 10 :
        text += "0%d ~ "%m
    else :
        text += "%d ~ "%m
    m += 1
    if m < 10 :
        text += "0%d月\n\n"%m
    else :
        text += "%d月\n\n"%m

    k=[  "特別獎     : " 
        ,"特獎         : " 
        ,"頭獎         : " 
        ,"增開六獎 : "
    ]

    for x in range(0 ,4):
        text += k[x]
        text += i[x]
        text += "\n"

    return text

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
    def is_going_to_bmi(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text.lower() == 'bmi'

    def is_going_to_bmi_height(self, update):
        global bmi_state
        global bmi_get_weight

        if bmi_state == -1 :
            try:
                bmi_get_weight = float(update.message.text)
                if bmi_get_weight == 0:
                    bmi_state = -1
                    return False
                bmi_state = 1
                return True
            except ValueError:
                bmi_state = -1

        elif bmi_state == 1:
            try:
                bmi_get_weight = float(update.message.text)
                if bmi_get_weight == 0:
                    bmi_state = -1
                    return False
                return True
            except ValueError:
                bmi_state = -1
            
        return False

    def is_going_to_bmi_show(self, update):
        global bmi_state
        global bmi_get_height

        if bmi_state == -2 :
            try:
                bmi_get_height = float(update.message.text)
                if bmi_get_height == 0:
                    bmi_state = -2
                    return False
                bmi_state = 2
                return True
            except ValueError:
                bmi_state = -2

        elif bmi_state == 2:
            try:
                bmi_get_height = float(update.message.text)
                if bmi_get_height == 0:
                    bmi_state = -2
                    return False
                return True
            except ValueError:
                bmi_state = -2

        return False

    def is_going_to_bmi_error(self, update):
        global bmi_state

        if bmi_state == -2 or bmi_state == -1:
            return True
            
        return False

    def is_going_to_photo(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text.lower() == 'photo'

    def is_going_to_photo_beauty(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text.lower() == '1'

    def is_going_to_photo_hell(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text.lower() == '2'

    def is_going_to_photo_beauty_candice(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text.lower() == '1'

    def is_going_to_photo_beauty_deer(self, update):
        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        return text.lower() == '2'

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
        return text.lower() == '3'

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
        global OX

        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False
        if OX == 1:
            return text.lower() == "exit"
        elif OX == 2:
            return text.lower() == "n"

    def is_going_to_receipt(self, update):

        if hasattr(update.message ,'text'):
            text = update.message.text
        else:
            return False

        return text.lower() == "receipt"

    def is_going_to_hint(self, update):
        global root
        if root == 1:
            return True
    
#######################################################################
    def on_enter_bmi(self, update):
        global bmi_state
        global root
        root = 0
        update.message.reply_text("Please give me your \" Weight \" in kilograms ")
        bmi_state = 1;
        #self.go_back(update)

    def on_exit_bmi(self, update):
        print('Leaving weight')

#######################################################################
    def on_enter_bmi_height(self, update):
        global bmi_state
        update.message.reply_text("Please give me your \" Height \" in centimeters ")
        bmi_state = 2;
        #self.go_back(update)

    def on_exit_bmi_height(self, update):
        print('Leaving height')

#######################################################################
    def on_enter_bmi_show(self, update):
        global bmi_state
        global bmi_get_height
        global bmi_get_weight

        b = bmi_get_weight / ((bmi_get_height/100)**2)
        
        if b < 16.5 or b > 31.5 :
            n = '(免役體位)'
        elif ( 16.5 <= b and b <17)  or ( 31 < b and b <= 31.5 ) :
            n = '(替代役體位)'
        else :
            n ='(常備役體位)'
        text  = "Here is yuor BMI : \n%.2f     "%b+n+"\n\n體位- - - - - - - - BMI範圍 - - - - - - - - 身高相對體重\n\n"
        k2 = ((bmi_get_height/100)**2)*16.5
        text += "免役體位          BMI＜16.5               　＜%.2f\n"%k2
        k1 = k2 
        k2 = ((bmi_get_height/100)**2)*17.0
        text += "替代役體位      16.5≦ BMI＜17       %-7.2f ~ %7.2f\n"%(k1 ,k2)
        k1 = k2 
        k2 = ((bmi_get_height/100)**2)*31
        text += "常備役體位      17≦BMI≦31            %-7.2f ~ %7.2f\n"%(k1 ,k2)
        k1 = k2 
        k2 = ((bmi_get_height/100)**2)*31.5
        text += "替代役體位      31＜BMI≦31.5        %-7.2f ~ %7.2f\n"%(k1 ,k2)
        k1 = k2 
        text += "免役體位          31.5＜BMI               　%.2f＜\n"%k1


        update.message.reply_text(text)
        
        bmi_state = 0;
        self.go_back(update)

    def on_exit_bmi_show(self, update):
        print('Leaving bmi')

#######################################################################
    def on_enter_bmi_error(self, update):
        if bmi_state == -1 :
            update.message.reply_text("Wrong Input!\nPlease give me your \" Weight \" in kilograms \" AGAIN \"")
        elif bmi_state == -2:
            update.message.reply_text("Wrong Input!\nPlease give me your \" Height \" in centimeters \" AGAIN \"")

    def on_exit_bmi_error(self, update):
        print('Leaving bmi error')

#######################################################################
    def on_enter_photo(self, update):
        global root
        root = 0

        update.message.reply_text("Which kind of photo do you want?\nPlease type the number :\n1 : Beauty\n2 : 通往地獄的大門\n3 : Leave photo")

    def on_exit_photo(self, update):
        print('Leavephoto')

#######################################################################
    def on_enter_photo_beauty(self, update):

        update.message.reply_text("Whose photo do you want?\nPlease type the number :\n1 : Candice\n2 : Deer\n3 : Leave photo")
         

    def on_exit_photo_beauty(self, update):
        print('Leaving beauty')

#######################################################################
    def on_enter_photo_beauty_candice(self, update):
        global id_chat
        n = random.randint(1 ,3)
        url = './pic/beauty/candice/%s.jpg'%str(n)
        __main__.bot.send_photo(chat_id= id_chat ,photo=open(url, 'rb'))
        self.go_back(update)

    def on_exit_photo_beauty_candice(self, update):
        print('Leaving Candice')

#######################################################################
    def on_enter_photo_beauty_deer(self, update):
        global id_chat
        n = random.randint(1 ,3)
        url = './pic/beauty/deer/%s.jpg'%str(n)
        __main__.bot.send_photo(chat_id= id_chat ,photo=open(url, 'rb'))
        self.go_back(update)

    def on_exit_photo_beauty_deer(self, update):
        print('Leaving Deer')

#######################################################################
    def on_enter_photo_hell(self, update):
        global id_chat
        n = random.randint(1 ,12)
        url = './pic/hell/%s.jpg'%str(n)
        __main__.bot.send_photo(chat_id= id_chat ,photo=open(url, 'rb'))
        self.go_back(update)
        
    def on_exit_photo_hell(self, update):
        print('Leaving Hell')

#######################################################################
    def on_enter_leave_photo(self, update):
        update.message.reply_text("Leave photo")
        self.go_back(update)

    def on_exit_leave_photo(self, update):
        print('Leaving photo')

#######################################################################
    def on_enter_state3(self, update):
        update.message.reply_text("I'm just here for test 😂")
        
        __main__.bot.send_sticker(chat_id= id_chat ,sticker = 'CAADAgADfgUAAvoLtghVynd3kd-TuAI')
        self.go_back(update)

    def on_exit_state3(self, update):
        print('Leaving state3')


#######################################################################
    def on_enter_ooxx(self, update):
        global puzzle
        global OX 
        global id_message

        global root
        root = 0

        if OX != 1:
            OX = 1
            puzzle  = [['_' for x in range(3)] for y in range(3)] 

            keyboard = []
            
            for x in range (0, 3):                     
                new = []                  
                for y in range (0, 3):  
                    foo = InlineKeyboardButton("%s"%puzzle[x][y], callback_data="%s"%str(x*3+y))  
                    new.append(foo)  
                keyboard.append(new)  
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            id_message = __main__.bot.send_message(chat_id= id_chat,text='You go first:\n\nType exit to leave the game', reply_markup=reply_markup).message_id
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
        global id_chat
        global id_message
        
        if OX == 1:
            __main__.bot.edit_message_text(text = 'Quit Game',
                                chat_id=id_chat,
                                message_id=id_message)
        else :
            update.message.reply_text("Leave OOXX")
        OX = 0

        self.go_back(update)

    def on_exit_state5(self, update):
        print('Leaving state5')
#######################################################################
    def on_enter_hint(self, update):       
        global hint_text
        
        update.message.reply_text(hint_text)
        self.go_back(update)

    def on_exit_hint(self, update):
        print('Leaving hint')

#######################################################################
    def on_enter_receipt(self, update):       
        now = datetime.datetime.now()
        
        year  = now.year
        month = now.month
        day   = now.day
        ran = 3

        if month%2 == 0:
            month-=1
            
        elif  day < 25:
            tmp = get_next_month(year ,month)
            year = tmp[0]
            month = tmp[1]

        y=[]
        m=[]
        for x in range(0 ,ran) :
            tmp = get_next_month(year ,month)
            year = tmp[0]
            month = tmp[1]
            y.append(year)
            m.append(month)

        text=""
        for x in range(0 ,ran) :
            i = get_receipt_number(y[x] ,m[x])
            text += make_receipt_text(y[x] ,m[x] ,i)
            text += "\n\n"
            
        update.message.reply_text(text)
        self.go_back(update)

    def on_exit_receipt(self, update):
        print('Leaving receipt')


#######################################################################
    def on_enter_user(self, update):       
        global root
        root = 1
        
        print('Entering user')

    def on_exit_user(self, update):
        print('Leaving user')
