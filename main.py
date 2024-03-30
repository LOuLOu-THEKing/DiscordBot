import discord
from discord.ext import commands
import mysql.connector as sqlc
import random
from timeit import default_timer as timer
from content import Help, GameList, Dm_Content

intents = discord.Intents.all()

client = commands.Bot(command_prefix="!", intents=intents)


#mysql database for showing leaderboards
connect = sqlc.connect(
  host="localhost",
  user="root",
  password="fgHfgH12@"
)

cur = connect.cursor()
cur.execute("use mindbreaker")


# opening sentence file for !tst & necessary vars
chek = True
f = open(r"sentence.txt", 'r')
sentences = f.readlines()
sentence = ''
f.close()
typespd = ''


# <text_file> with different words for hangman (initializing that)
f = open('hangman.txt', 'r')
data = f.read()
f.close()
data = data.split('\n')
word = random.choice(data)
gameover = True
if gameover == True:
    data_to_guess = ''
listword = list(word)
limit = 5
person = ''
limith = 3

# initiation vars required !tictactoe
player1 = ""
player2 = ""
turn = ""
gameOver = True
board = []

winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]



# Readyyy!!!
@client.event
async def on_ready():
    print('Ready to go as {0.user} !!!'.format(client))
#commands
# initiating command code for help
@client.command()
async def commandhelp(ctx):
    await ctx.send(Help)

#provides a list of games
@client.command()
async def gmlt(ctx):
    await ctx.send(GameList)

#type speed test
@client.command()
async def tst(ctx):
    global chek
    global sentence
    chek = False
    if chek == False:
        sentence = random.choice(sentences)
        await ctx.send(f'Welcome to Type Speed test,{ctx.author.mention}!!!!')
        await ctx.send('Below is the sentence you have to type:')
        await ctx.send(sentence)

        def check(m):
            global typespd
            if m.author == client.user:
                return
            elif m.author == ctx.author:
                if m.channel.id == ctx.channel.id:
                    typespd = m.content
                    return typespd
                    timer()


        # defining function type speed test (tst()) for determining the final time
        def tst():
            i = 0
            count = 0
            error = 0
            global typespd
            global sentence
            if len(typespd) >= len(sentence):
                for i in range(len(sentence)):
                    if typespd[i] == sentence[i]:
                        count += 1
                    else:
                        error += 1
            elif len(typespd) < len(sentence):
                for j in range(len(typespd)):
                    if typespd[i] == sentence[i]:
                        count += 1
                    else:
                        error += 1
            end = timer()
            a, b, c = count / end, error / end, (count + error) / end
            return a, b, c
    if chek == True:
        await ctx.send('Something is wrong. Please Try again later.')

    await client.wait_for('message', check=check)
    a, b, c = tst()
    if a*10 < 5 and b < 0.5:
        await ctx.send("Congratulations! you got 10 points for getting the time less than 5 seconds.")
        cur.execute("""update lb set points = points + 10 where username = '{}'""".format(ctx.author.name))
        connect.commit()
    a = 'correct cpm: ' + str((round(a *10 , 3))) + ' secs'
    b = 'error cpm: ' + str(((round(b * 10 , 3)))) + ' secs'
    c = 'total cpm: ' + str(((round(c * 10 , 3)))) + ' secs'
    await ctx.send(a + '\n' + b + '\n' + c)


#tic tac toe with another player
@client.command()
async def tictactoe(ctx, p1: discord.Member):
    global count
    global player1
    global player2
    global turn
    global gameOver

    if gameOver:
        global board
        board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        turn = ""
        gameOver = False
        count = 0

        player1 = ctx.author
        player2 = p1

        # print the board
        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]

        # determine who goes first
        num = random.randint(1, 2)
        if num == 1:
            turn = player1
            await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
        elif num == 2:
            turn = player2
            await ctx.send("It is <@" + str(player2.id) + ">'s turn.")

    else:
        await ctx.send("A game is already in progress! Finish it before starting a new one.")

#tic tac toe placing command
@client.command()
async def place(ctx, pos: int):
    global turn
    global player1
    global player2
    global board
    global count
    global gameOver

    if not gameOver:
        mark = ""
        if turn == ctx.author:
            if turn == player1:
                mark = ":regional_indicator_x:"
            elif turn == player2:
                mark = ":o2:"
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:":
                board[pos - 1] = mark
                count += 1

                # print the board
                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winningConditions, mark)
                if gameOver == True:
                    await ctx.send(mark +"wins!")
                    if turn != client.author:
                        await ctx.send(turn.name + " wins 10 points!")
                        query = ("update lb set points = points + 10 where username = '{}'".format((turn.name)))
                        cur.execute(query)
                        connect.commit()
                elif count >= 9:
                    gameOver = True
                    await ctx.send("It's a tie!")
                    await ctx.send("uhoh! No one gets any points though :(")

                # switch turns & the bot chooses it's tile!
                if turn == player1:
                    turn = player2
                    if gameOver == False:
                        await ctx.send("It is <@" + str(player2.id) + ">'s turn.")
                        if turn == client.user:
                            while True:
                                number = random.randint(0, 8)
                                print(number)
                                if board[number + 1] == ":white_large_square:":
                                    board[number + 1] = ":o2:"
                                    print(board)
                                    for x in range(len(board)):
                                        if x == 2 or x == 5 or x == 8:
                                            line += " " + board[x]
                                            await ctx.channel.send(line)
                                            line = ""
                                        else:
                                            line += " " + board[x]
                                    break
                            turn = player1
                elif turn == player2:
                    turn = player1
                    if gameOver == False:
                        await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
            else:
                await ctx.send("Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile.")
        else:
            await ctx.send("It is not your turn.")
    else:
        await ctx.send("Please start a new game using the !tictactoe or !ttt command.")

def checkWinner(winningConditions, mark):
    global gameOver
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True

# tic tac toe with a bot
@client.command()
async def ttt(ctx):
    global count
    global player1
    global player2
    global turn
    global gameOver
    if gameOver:
        global board
        board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        turn = ""
        gameOver = False
        count = 0

        player1 = ctx.author
        player2 = client.user

        # print the board
        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]
        # determine who goes first  
        num = random.randint(1, 2)
        if num == 1:
            turn = player1
            await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
        elif num == 2:
            turn = player2
            await ctx.send("It is <@" + str(player2.id) + ">'s turn.")
            if turn == client.user:
                while True:
                    number = random.randint(0, 8)
                    print(number)
                    if board[number] == ":white_large_square:":
                        break
                if board[number] == ":white_large_square:":
                    board[number] = ":o2:"
                    for x in range(len(board)):
                        if x == 2 or x == 5 or x == 8:
                            line += " " + board[x]
                            await ctx.channel.send(line)
                            line = ""
                            break
                        else:
                            line += " " + board[x]
                            break
                turn = player1
    else:
        await ctx.send("A game is already in progress! Finish it before starting a new one.")

@client.command()
async def hangman(ctx):
    global data_to_guess
    global word
    global data
    global gameover
    global person
    global limit
    person = ctx.author
    limit = 5
    data_to_guess = ''
    gameover = False
    if word != '':
        word = random.choice(data)

    await ctx.send(
        'Welcome to Hangman! Use the syntax, "!guess <letter> or !guess <word> to find the answer!')
    # random choice of word
    # embed buttons
    embed = discord.Embed(title="Hangman!", description="Guess The Letters!!!")
    embed.set_author(name= client.user,
                     icon_url="https://cdn.discordapp.com/attachments/955794842405994576/956796656957923388/2022-03-25_1.png")
    for i in range(len(word)):
        data_to_guess += '- '

    embed.add_field(name=data_to_guess, value="You got 5 chances!", inline=False)

    await ctx.send(embed=embed)
    # define check function


@client.command()
async def guess(ctx, str):
    global gameover
    global word
    global data_to_guess
    global limit
    global person
    if gameover == False:
        if ctx.author == person:
            if str not in word and len(str)>=1:
                limit -= 1
            if str == word:
                await ctx.send('yayyy!!!! you got the answer correct!')
                await ctx.send('you get 15 points for getting it correctly!')
                query = "update lb set points  = points + 15 where username = '{}'".format(ctx.author.name)
                print(ctx.author.name)
                cur.execute(query)
                connect.commit()
                gameover = True
            elif len(str) == 1:
                embed = discord.Embed(title="Hangman!", description="Guess The Letters!!!")
                embed.set_author(name= client.user,
                                 icon_url="https://cdn.discordapp.com/attachments/955794842405994576/956796656957923388/2022-03-25_1.png")
                listdata_to_guess = list(data_to_guess)
                if word.count(str) == 1:
                    i = word.index(str)
                    listdata_to_guess[2 * i] = word[i]
                elif word.count(str) == 2:
                    i = word.rindex(str)
                    j = word.index(str)
                    listdata_to_guess[2*i] = word[i]
                    listdata_to_guess[2 * j] = word[j]
                elif word.count(str) > 2:
                    data_to_guess = ''
                    for i in word:
                        if i == str:
                            data_to_guess += str + ' '
                        else:
                            data_to_guess += '- '
                    listdata_to_guess = list(data_to_guess)
                data_to_guess = ''
                for i in listdata_to_guess:
                    data_to_guess += i
                embed.add_field(name=data_to_guess, value="You got {} chances!".format(limit), inline=False)
                await ctx.send(embed=embed)
            elif len(str) > 1:
                await ctx.send('Please guess only 1 letter at a time, or the entire word!')
                limit -= 1
        else:
            await ctx.send("This is not your chance. Please start another one.")
    elif gameover is True:
        await ctx.send('uhoh! it seems the game has stopped. Please start again using "!hangman" command.')




    if data_to_guess.split() == list(word) :
        await ctx.send('yayy!!! you got the answer correct!')
        await ctx.send('you get 15 points for getting it correctly!')
        query = "update lb set points  = points + 15 where username = '{}'".format(ctx.author.name)
        cur.execute(query)
        connect.commit()
        gameover = True
        data_to_guess = ''
        limit = 5
    if limit == 0:
        await ctx.send('uhoh, it seems you got 5 wrong guesses. The word is {}! Try again!'.format(word))
        gameover = True
        data_to_guess = ''
        limit = 5

@client.command()
async def hint(ctx):
    global gameover
    global word
    global data_to_guess
    global limit
    global person
    global limith
    if gameover == False:
        if limith == 0:
            await ctx.send('You have no hints left.')
        elif ctx.author == person:
            while True:
                x = random.choice(word)
                print(x)
                print(data_to_guess)
                if x not in data_to_guess:
                    await ctx.send('There is a letter '+ x + ' in this word!')
                    list_dtg = list(data_to_guess)
                    i = word.index(x)
                    list_dtg[2 * i] = word[i]
                    data_to_guess = ''
                    for i in list_dtg:
                        data_to_guess += i
                    embed = discord.Embed(title="Hangman!", description="Guess The Letters!!!")
                    embed.set_author(name=client.user,
                                     icon_url="https://cdn.discordapp.com/attachments/955794842405994576/956796656957923388/2022-03-25_1.png")
                    embed.add_field(name=data_to_guess, value="You got {} chances!".format(limit), inline=False)
                    await ctx.send(embed=embed)
                    await ctx.send('now you have got only '+ str(limith - 1) + ' hints')
                    limith -= 1
                    break
                else:
                    continue
    else:
        if limit == 0:
            limith = 3

@client.command()
async def lb(ctx):
    cur.execute("select * from lb where username = '{}' order by points DESC".format(ctx.author.name))
    data = cur.fetchall()
    for i in data:
        await ctx.send('rank = '+ str(i[0]))
        await ctx.send('username = ' + i[1])
        await ctx.send('points =' + str(i[2]))





#errors
@tictactoe.error
async def tictactoe_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention a player to play with for this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to mention/ping player (ie. <@688534433879556134>).")

@place.error
async def place_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a position you would like to mark.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to enter an integer.")

@tst.error
async def tst_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('Please Type "!tst" and try again!')
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Oops! there is an error! Please try again!')

@hangman.error
async def hangman_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('Please Type "!hangman" and try again!')
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Oops! there is an error! Please try again!')
@guess.error
async def guess_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('Oops! there is an error! Please try again!')
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please Type "!guess <a letter>" or "!guess <the word> and try again!')



#events (sending message when member joins or leaves
@client.event
async def on_member_join(member):
    print(member)
    newUserMessage = """ Hii!!! Welcome {} """.format(member.name) + Dm_Content  # DMs the person
    query = ("insert into lb(username, points) values('{}', 0)".format(member.name))
    cur.execute(query)
    connect.commit()
    await member.send(newUserMessage)


@client.event
async def on_member_remove(member):

    Userleft = '''I see {} left :sob: 
  We hope they had a fun time they were there ;-;'''.format(member.name)
    await member.send(Userleft)
    query = ("delete from lb wh ere username = '{}'".format(member.name))
    cur.execute(query)
    connect.commit()

my_secret = ''
client.run(my_secret)
