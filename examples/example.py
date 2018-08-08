# Relative path
import sys
sys.path.append('..')
from responds import Responder
from logger import Logger

# Please notice that this class is only an example and will not be added
# to the wechatbot's responders map. To add one, you need to create your
# class under `responds.py` file in the following format
# If you wamt to see the result of the following codes, copy them
# to the `responds.py` file

# Dont forget to add the new responder's description to the HelpResponder,
# to let users know how to use it

class BasicResponder(Responder):
    """
    BasicResponder can handle the case that the keyword only has one word,
    like 'weather', 'help' and so on.
    """
    # The constructor SHOULD NOT have any arguments
    def __init__(self):
        # It is recommend to use logger to do log, for debug purpose
        self.logger = Logger("BasicResponder")
        self.logger.log("Initialized new BasicResponder")

    # The key function return the keyword of this responder. When the
    # wechatbot detects keyword, it will find the corresponding responder
    # for response. In this case, when user send 'basic', the wechatbot will
    # then find this responder
    # THIS METHOD MUST BE OVERRIDDE
    def key(self):
        return "basic"

    # The response of this responder, you can customize any responses. The
    # return type must be str
    # THIS METHOD MUST BE OVERRIDDE
    def respond(self):
        return self._logic()

    # Return False indicates that this responder can only handle basic requests
    # All basic responder must return False
    # THIS METHOD MUST BE OVERRIDDE
    def is_complex(self):
        return False

    # You can do various kinds of logics here, such as using API to get
    # information or so on.
    # This method is just an example, represents the logic part
    def _logic(self):
        return "After logic processing, return basic response"


class ComplexResponder(Responder):
    """
    ComplexResponder can handle complex requests that need the input details.
    For instance, `note add {your_note}` require three parts: key, which is
    the keyword `note`, action, which is `add`, and detail which is
    `{your_note}`.
    """
    def __init__(self):
        # It is recommend to use logger to do log, for debug purpose
        self.logger = Logger("BasicResponder")
        self.logger.log("Initialized new ComplexResponder")
        # Store variables
        self.puid = None
        self.action = None
        self.detail = None

    # Same as BasicResponder, return a keyword in str
    # THIS METHOD MUST BE OVERRIDDE
    def key(self):
        return "complex"

    # Return a list of valid actions. As explained, actions are a word that
    # following the keyword. WechatBot will check if user's request contains
    # a valid action, it will compare the action with this list.
    # THIS METHOD MUST BE OVERRIDDE
    def actions(self):
        return ["action1", "action2"]

    # Same as BasicResponder, return a response in str after
    # processing some logics
    # THIS METHOD MUST BE OVERRIDDE
    def respond(self):
        return self._logic()

    # Return True to indicates that this responder can handle complex requests
    # All complex responder must return True
    # THIS METHOD MUST BE OVERRIDDE
    def is_complex(self):
        return True

    # Receive varibales from wechatbot, you can either choose to use them or not
    # THIS METHOD MUST BE OVERRIDDE
    def receive(self, puid, action, detail):
        self.puid = puid        # A unique id for each user
        self.action = action    # An action in action list
        self.detail = detail    # Details after action

    # You can do various kinds of logics here, such as using API to get
    # information or so on.
    # This method is just an example, represents the logic part
    def _logic(self):
        return "puid = " + self.puid + ", action = " + self.action +\
                ", detail = " + self.detail
