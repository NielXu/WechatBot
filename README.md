# Description
WechatBot is a tool that built on the popular social app named 'Wechat'. It can let a wechat account become a 'bot', which can receive requests from users and return responses based on the request type. It helpes us in little things such as knowing the weather today or tracking some stocks. All we need to do is just send the request and we will get response by the bot in a second.

# Get started
Follow these steps to let your wechat account become a WechatBot:

1. Use `$ pip install -U wxpy` to install the `wxpy` package
2. Use `$ pip install --upgrade google-cloud-translate` to install the google translate package
3. To use the weather feature, get a free [OpenWeatherMap API key](https://openweathermap.org/api) and replace `{your_api_key}` in `responds.WeatherResponder` to your API key
4. To use the stock feature, get a free [Alphavantage API key](https://alphavantage.co/support/#api-key) and replace `{your_api_key}` in `responds.StockResponder` to your API key
5. To use the translate feature, check out [Google translate API](https://cloud.google.com/translate/docs/reference/libraries#client-libraries-install-python), download the json and setup the environmental variable
6. Run script `$python wechatbot.py`
7. Scan the QR code that showed up on the screen with your wechat
8. Done! Send `help` to yourself for instructions (need to enable `allow_self`)

# Control variables
There are few features that can be turned on or off in `wechatbot.py`:

- `do_log = True`: set True to show logs on the console, this variable only controls the wechatbot logger and will not affect other classes
- `send_greet = False`: set True to send greeting message to users when the bot go online
- `send_bye = False`: set True to send goodbye message to users when the bot go offline
- `restrict = True`: set True to let wechatbot only respond to listed users
- `allow_self = True`: set True to allow wechatbot to respond to your own requests
- `auto_mark = False`: set True to automatically mark all messages the wechatbot received as read
- `username_list = []`: if the restrict mode is on, wechatbot will search for users with the given names on freind list, only those users can access the bot
- `greeting = ''`: if the send greeting message mode is on, this message will be sent to users
- `bye = ''`: if the send goodbye message mode is on, this message will be sent to users

# Basic requests
Here are some basic requests, send them to the wechatbot to test them out:

- `help`: show all requests and their explanations
- `weather`: show real-time weather information
- `note add {your_note}:` let wechatbot to save the given notes under `resources/user_notes.json`, each user has a unique ID as key
- `note show {index}`: show note at the given index
- `note show all`: show all the notes that user has saved
- `note del {index}`: delete note that saved at the given index
- `note del all`: delete all the notes that user has saved
- `stock track {symbol}`: show real-time stock information based on the given symbol
- `stock history {date} {symbol}`: show stock's history information
- `translate {lang_code} {content}:` show the translation of the content

# Custom Responder
Other than basic requests, you can create your own requests and responses easily. All you need to do is just inherit the `Responder` abstract class, override methods and that's it. You do not need to add responder to wechatbot manually, the bot will scan all the subclasses of `Responder` and automatically invoke `respond()` when the corresponding request was received. See `examples/example.py` for an complete example.
