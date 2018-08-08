from responds import *
from wxpy import *
from logger import *

#
#   Boolean that controls some features
#
do_log = True       # show log on console while the bot is runing, this
                    # variable can only control WechatBot
send_greet = False   # send greeting message to users when online
send_bye = False     # send bye message to users when offline
restrict = True     # Restriction, only users on list can access the bot
allow_self = True   # allow access bot by yourself
auto_mark = False   # Automatically mark messages as read

# 39L1WOFKTYSACMQO

#
#   Variables
#
logger = Logger("WechatBot", do_log)
logger.log("Initializing WechatBot")
responder_list = [cls() for cls in Responder.__subclasses__()]
responder_map = {} # A map that stores in format 'responder_keyword':responder
# Provide user names for restriction
username_list = [
                ]
# Only users in this list can access bot, if restrict is True
users = None
# Greeting message
greeting = "WechatBot v0.1b is online now, send help for more informations"
# Bye message
bye = "WechatBot v0.1b is offline now, thank you for using :)"
# Fill dict
for r in responder_list:
    responder_map[r.key()] = r


#
#   Scripts
#
logger.log("Activating WechatBot")
bot = Bot(cache_path=True)  # Allow cache, avoid scanning QR too many times
bot.enable_puid()
bot.auto_mark_as_read = auto_mark


#
#   Methods
#
def get_responder(sender, request):
    """
    Get responder corresponding to the given keyword in request
    There are two kinds of format:
        simple: weather, help...
            return 'weather', 'help'...
        complex: note add blablabla, note del blablabla
            return ['note','add','blablabla']...
    Return None if input str is not a valid key
    Return Responder if keyword is matched
    """
    splitter = request.split(" ")
    main_key = splitter[0]
    # Make sure main key is in key list
    if main_key in responder_map:
        r = responder_map[main_key]
        # Handle simple request
        if len(splitter) == 1 and not r.is_complex():
            logger.log("Request type: " + main_key)
            return r
        # Handle complex request
        # Make sure the responder can handle complex request
        elif len(splitter) >= 3 and r.is_complex():
            logger.log("Request type: " + main_key)
            a = splitter[1]             # Action
            d = " ".join(splitter[2:])  # Detail
            logger.log("Request action: " + a)
            logger.log("Request detail: " + d)
            # Make sure action is valid
            if a in r.actions():
                r.receive(sender.puid, a, d)
                return r
    return None

def get_users(username):
    """
    Search for users with the given username. If the given
    username does not exist, it will be ignored
    Return a list of user object in wxpy as result
    """
    if restrict:
        users = []
        friends = bot.friends()
        for user in username:
            search = friends.search(user)
            if len(search) > 0:
                users.append(search[0])
        if allow_self:
            users.append(bot.self)
        return users
    return None
users = get_users(username_list)

def send_to_users(msg):
    """
    Send message to users. If restrict is on, send to user_list,
    otherwise, send to all users(be careful)
    """
    if restrict:
        for user in users:
            user.send(msg)
    else:
        friends = bot.friends()
        for f in friends:
            f.send(msg)


#
#   Bot register
#
logger.log("Param: go_log="+str(do_log))
logger.log("Param: send_greet="+str(send_greet))
logger.log("Param: send_bye="+str(send_bye))
logger.log("Param: restrict="+str(restrict))
logger.log("Param: allow_self="+str(allow_self))
logger.log("Accepet users(if None, means all users)="+str(users))
logger.log("WechatBot activated")
# Sending welcome message
if send_greet:
    send_to_users(greeting)

@bot.register(chats=users, msg_types=TEXT, except_self=not allow_self)
def reqeust_respond(msg):
    logger.log("Request from: " + str(msg.sender))
    responder = get_responder(msg.sender, msg.text)
    if responder is not None:
            respond = responder.respond()
            if respond is not None:
                logger.log("Respond: " + respond)
                logger.span()
                return respond
    logger.log("Not a valid request, ignored")
    logger.span()

# keep thread alive
embed()
# Sending goodbye message
if send_bye:
    send_to_users(bye)
logger.log("WechatBot deactivated")
