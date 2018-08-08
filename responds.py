import time
import urllib.request
import json
import os
import datetime
from logger import *
from abc import ABC, abstractmethod
from google.cloud import translate

class Responder(ABC):
    """
    The parent class of all responder. Inheriting this class allow script
    to create instance of the reponder by reflection. The responder that
    did not inherit this class will not be accessible.
    All responders should not have any arguments in constructor.
    All responders need to implement method key()
    All responders need to implement method respond()
    All responders need to implement method is_complex()
    method receive() is optional and only useful when handling complex request
    method actions() is optional and only useful when handling complex request
    It is recommended to use logger to keep track of requests and responds
    """
    @abstractmethod
    def key(self):
        "return keyword corresponding to this responder"

    @abstractmethod
    def respond(self):
        """
        return respond that will send to user, in str format
        return None if the request is not valid
        """

    @abstractmethod
    def is_complex(self):
        "return True if it can handle compelx reqeust, False otherwise"

    def receive(self, puid, action, detail):
        "let this responder to receive user puid and an action with detail"

    def actions(self):
        "return a list of actions that this responder can handle"


class WeatherResponder(Responder):
    "WeatherResponsder retrieve informations from OpenWeatherMap."
    def __init__(self):
        """
        Var: weather_base: The base url of the OpenWeatherMap request
        Var: weather_appid: full weather_appid url
        Var: weather_city: full weather_city url
        Var: weather_unit: full weather_unit url
        Var: weather_full_url: The full request url contains all above
        Var: data: The data in dict format
        """
        # The base url of the OpenWeatherMap
        self.weather_base = "http://api.openweathermap.org/data/2.5/weather?"
        # Your own OpenWeatherMap appid
        self.weather_appid = "appid={your_api_key}"
        # Your city id on openweathermap
        self.weather_city = "id=6167865"
        self.weacher_unit = "units=metric"
        # The full request url
        self.weather_full_url = self.weather_base \
                                + self.weather_city + "&"\
                                + self.weather_appid + "&"\
                                + self.weacher_unit
        self.logger = Logger("WeatherResponder")
        self.logger.log("Iniaialized new WeatherResponder")

    def is_complex(self):
        return False

    def key(self):
        return "weather"

    def respond(self):
        data = self._retrieve_weather()
        condition = data['weather'][0]['main']
        condition_detail = data['weather'][0]['description']
        temp = str(data['main']['temp'])
        min_temp = str(data['main']['temp_min'])
        max_temp = str(data['main']['temp_max'])
        return "City: Toronto\n"+\
                "Current temperature: " + temp + "°C\n"+\
                "Lowest temperature: " + min_temp + "°C\n" +\
                "Highest temperature: " + max_temp + "°C\n" +\
                "Condition: "+condition + "\n" +\
                "Condition detail: "+condition_detail+"\n"

    def _retrieve_weather(self):
        """
        Retrieve the weather informations from OpenWeatherMap. If the last
        request was in ten mins, return the same result, otherwise, retrieve
        the new result again
        """
        # If it is already ten mins after, retrieve new data
        if self._over_last_retrieve_time():
            self.logger.log("Retrieve new weather data")
            with urllib.request.urlopen(self.weather_full_url) as url:
                data = json.loads(url.read().decode())
            self._save_json(data)
            self._save_last_retrieve_time()
            return data
        else:
            self.logger.log("Using saved weather data")
            return self._read_json()

    def _read_json(self):
        "Read the json file"
        self.logger.log("Reading json 'weather_temp.json'")
        with self._open_weather_temp("r") as f:
            data = json.load(f)
        return data

    def _save_json(self, data):
        "Save the respond json file to local temp file"
        self.logger.log("Saving data to json 'weather_temp.json'")
        with self._open_weather_temp("w") as f:
            json.dump(data, f)

    def _over_last_retrieve_time(self):
        "Return True if last retrieve time is over ten mins, false otherwise"
        # Convert ten mins to seconds
        ten_mins = 10 * 60
        # Calculate the difference
        now = time.time()
        last = self._get_last_retrieve_time()
        if now - last > ten_mins:
            return True
        return False

    def _save_last_retrieve_time(self):
        "Save current time as last retrieve time, usually save after requesting"
        self.logger.log("Updaed last retrieved time in 'weather_retrieve_time'")
        with self._open_weather_retrieve_time("w") as f:
            f.write(str(time.time()))

    def _get_last_retrieve_time(self):
        "Get last retrieve time as float"
        with self._open_weather_retrieve_time("r") as f:
            time = float(f.readline())
        return time

    def _open_weather_temp(self, mode):
        "Return opened file, remember to close"
        return open("resources/weather_temp.json", mode)

    def _open_weather_retrieve_time(self, mode):
        "Return opened file, remember to close"
        return open("resources/weather_retrieve_time", mode)


class HelpResponder(Responder):
    "HelpResponder return str that help users to use the bot"
    def __init__(self):
        self.logger = Logger("HelpResponder")
        self.logger.log("Iniaialized new HelpResponder")

    def key(self):
        return "help"

    def is_complex(self):
        return False

    def respond(self):
        return "WechatBot receives requests and responds to them. The "+\
                "requests must strictly follow the syntax as shown below.\n" +\
                "Here are all the keywords. The following informations are "+\
                "in 'keyword': explaination format\n\n" +\
                "'weather': Get the real-time weather informations\n\n" +\
                "'note add [youtnotes]': Add notes and bot will save it. " +\
                    "Notes have their own indices, first will be 0 and "+\
                    "continue to increase as more notes being saved\n\n" +\
                "'note show [index]': View note by index, starts from 0. " +\
                    "If the note does not exist, will respond 'No note " +\
                    "found by the given index'\n\n" +\
                "'note show all': View all the notes you've saved "+\
                    "in the bot. In format: index: [younotes]. " +\
                    "Respond 'No notes found' If there is no note saved\n\n" +\
                "'note del [index]': Delete note by its index, if the note " +\
                    "does not exist, will respond 'No note found by the " +\
                    "given index'\n\n" +\
                "'note del all': Delete all the notes you have saved\n\n" +\
                "'note update [index] [yournotes]': Update the note that " +\
                    "you have saved by the given index. Will respond " +\
                    "'No note found by the given index' if the note " +\
                    "does not exist\n\n" +\
                "'stock track [stock symbol]': Get the real-time stock " +\
                    "informations by its symbol. Please notice that if the " +\
                    "stock market is closed today, it will return " +\
                    "'Stock market closed, no data given'\n\n" +\
                "'stock history [date] [stock symbol]': Get the history " +\
                    "stock data on a specific date. The date must be in " +\
                    "format 'yyyy-mm-dd'. And the max date it can track is " +\
                    "four months from today. For instance, if today is " +\
                    "Aug 1st, the oldest date is Apr 1st. If the stock " +\
                    "market was closed that day, it will return " +\
                    "'Stock market closed on [date], no data given'\n\n" +\
                "'translate [lang code] [sentence]': Translate the " +\
                    "given sentence to the given language. For " +\
                    "[lang code], check out https://sites.google.com/" +\
                    "site/tomihasa/google-language-codes"


class NoteResponder(Responder):
    """
    Note responder retrieve notes of corresponding user and return them.
    It can also save, delete or modify notes. The notes are saved based
    on the puid that provided by the wxpy.Bot and they are unique. Therefore,
    each user has separate notes and there are no conflicts between them
    """
    def __init__(self):
        self.logger = Logger("NoteResponder")
        self.logger.log("Iniaialized new NoteResponder")
        self.action = None
        self.detail = None
        self.puid = None

    def is_complex(self):
        return True

    def key(self):
        return "note"

    def respond(self):
        if self.action == "add":
            return self.add_respond(self.puid, self.detail)
        elif self.action == "show":
            if self.detail == "all":
                return self.shw_all_respond(self.puid)
            elif self.detail.isdigit():
                return self.shw_index_respond(self.puid, self.detail)
        elif self.action == "del":
            if self.detail == "all":
                return self.del_all_respond(self.puid)
            elif self.detail.isdigit():
                return self.del_index_respond(self.puid, self.detail)
        elif self.action == "update":
            return self.upd_respond(self.puid, self.detail)

    def receive(self, puid, action, detail):
        self.puid = puid
        self.action = action
        self.detail = detail

    def actions(self):
        return ["add", "del", "show", "update"]

    def add_respond(self, user_id, note):
        "Save notes and give respond"
        data = self._read_json()
        if note.isspace():
            return "Note cannot be empty"
        if user_id not in data:
            data[user_id] = []
        data[user_id].append(note)
        with self._open_notes("w") as f:
            json.dump(data, f)
        return "Successfully saved your note"

    def shw_all_respond(self, user_id):
        "Show all notes user have saved"
        data = self._read_json()
        if user_id not in data:
            return "No notes found"
        notes = data[user_id]
        if len(notes) == 0:
            return "No notes found"
        respond = ""
        for index in range(0, len(notes)):
            respond += str(index) + ": " + notes[index] + "\n\n"
        return respond

    def shw_index_respond(self, user_id, index):
        "Show note by index"
        iindex = int(index)
        data = self._read_json()
        if user_id not in data:
            return "No notes found by given index"
        notes = data[user_id]
        if len(notes) == 0:
            return "No notes found"
        if iindex >= len(notes):
            return "Index out of range, should be in [0, "+str(len(notes)-1)+"]"
        return notes[iindex]

    def del_all_respond(self, user_id):
        "Delete all notes"
        data = self._read_json()
        if user_id not in data:
            return "No notes found"
        data[user_id] = []
        with self._open_notes("w") as f:
            json.dump(data, f)
        return "Successfully deleted all the notes"

    def del_index_respond(self, user_id, index):
        "Delete note by index"
        iindex = int(index)
        data = self._read_json()
        if user_id not in data:
            return "No notes found"
        notes = data[user_id]
        if iindex >= len(notes):
            return "Index out of range, should be in [0, "+str(len(notes)-1)+"]"
        notes.pop(iindex)
        with self._open_notes("w") as f:
            json.dump(data, f)
        return "Successfully deleted note at index: " + index

    def upd_respond(self, user_id, detail):
        "Update note at index, replace old with new note"
        splitter = detail.split(" ")
        index = splitter[0]
        if index.isdigit():
            new_note = " ".join(splitter[1:])
            iindex = int(index)
            data = self._read_json()
            if user_id not in data:
                return "No notes found"
            notes = data[user_id]
            if iindex >= len(notes):
                return "Index out of range, should be in [0, "+\
                        str(len(notes)-1)+"]"
            notes[iindex] = new_note
            with self._open_notes("w") as f:
                json.dump(data, f)
            return "Successfully updated note at index: " + index

    def _read_json(self):
        "Return the data stores in json file"
        file = self._open_notes("r")
        data = json.load(file)
        file.close()
        return data

    def _open_notes(self, mode):
        return open("resources/user_notes.json", mode)


class StockResponder(Responder):
    """
    StockResponder will respond to user's the real-time stock informations
    based on the symbol that they enetered from alphavantage
    """
    def __init__(self):
        """
        Param: symbol: The symbol of the stock
        Param: base_url: The base url of the alphavantage website
        Param: function: The function that is requesting
        Param: api_key: Your custom api key
        Param: data: The data that responded by alphavantage
        """
        self.detail = None
        self.symbol = None
        self.base_url = "https://www.alphavantage.co/query?"
        self.function = "function=TIME_SERIES_DAILY"
        self.api_key = "apikey={your_api_key}"
        self.data = None
        self.action = None
        self.logger = Logger("StockResponder")
        self.logger.log("Initialized new StockResponder")

    def key(self):
        return "stock"

    def actions(self):
        return ["track", "history"]

    def is_complex(self):
        return True

    def respond(self):
        if self.action == "track":
            return self.today_respond()
        elif self.action == "history":
            return self.history_respond()

    def history_respond(self):
        "Respond to history stock"
        splitter = self.detail.split(" ")
        if len(splitter) != 2:
            return None
        date = splitter[0]
        self.symbol = splitter[1]
        if not self._valid_date(date):
            return "Invalid date, must be in format yyyy-mm-dd"
        self._retrieve_stock()
        if self._function_key() not in self.data:
            return "Invalid stock symbol"
        stocks = self.data[self._function_key()]
        if date not in stocks:
            return "Date too long ago or stock market was closed at: " + date
        history_stock = stocks[date]
        open = history_stock['1. open']
        high = history_stock['2. high']
        low = history_stock['3. low']
        close = history_stock['4. close']
        vol = history_stock['5. volume']
        return "Stock symbol: " + self.symbol +"\n" +\
                "Date: " + date + "\n" +\
                "Open: " + open + "\n" +\
                "High: " + high + "\n" +\
                "Low: " + low + "\n" +\
                "Close: " + close + "\n" +\
                "Volume: " + vol

    def today_respond(self):
        "Respond to today's stock tracking"
        self.symbol = self.detail
        if len(self.symbol.strip()) == 0:
            return None
        self._retrieve_stock()
        if self._function_key() not in self.data:
            return "Invalid stock symbol"
        stocks = self.data[self._function_key()]
        if self._current_date() not in stocks:
            return "Stock market closed, no data given."
        today_stock = stocks[self._current_date()]
        open = today_stock['1. open']
        high = today_stock['2. high']
        low = today_stock['3. low']
        close = today_stock['4. close']
        vol = today_stock['5. volume']
        return "Stock symbol: " + self.symbol +"\n" +\
                "Date: " + self._current_date() + "\n" +\
                "Open: " + open + "\n" +\
                "High: " + high + "\n" +\
                "Low: " + low + "\n" +\
                "Close: " + close + "\n" +\
                "Volume: " + vol

    def receive(self, puid, action, detail):
        "Receive symbol that user is searching for"
        self.detail = detail
        self.action = action

    def _valid_date(self, date_text):
        "Check if date is in format yyyy-mm-dd"
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def _function_key(self):
        "The function key, see alphavantage json for more informations"
        return "Time Series (Daily)"

    def _current_date(self):
        "Get current date in format yyyy-mm-dd"
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def _construct_full_url(self):
        "Construct full url"
        return self.base_url + self.function + "&symbol=" + self.symbol + "&"+\
                self.api_key

    def _retrieve_stock(self):
        "Retrieve stock informations, store json data"
        self.logger.log("Retrieve stock informations from alphavantage")
        full_url = self._construct_full_url()
        with urllib.request.urlopen(full_url) as url:
            self.data = json.loads(url.read().decode())


class TranslationResponder(Responder):
    """
    TranslationResponder is respondible for translating the given sentence to
    a different language.
    """
    def __init__(self):
        self.logger = Logger("TranslationResponder")
        self.logger.log("Initialized new TranslationResponder")
        self.codes = None
        self.target_lang = None
        self.detail = None
        self.client = None

    def key(self):
        return "translate"

    def respond(self):
        if not len(self.detail.strip()) == 0:
            return self._google_translate()

    def is_complex(self):
        return True

    def actions(self):
        "List of valid language codes"
        return ["af", "sq", "ar","be", "bg", "ca", "zh-CN", "zh-TW", "hr",
             "cs", "da", "nl", "en", "et", "tl", "fi", "fr", "gl", "de",
             "el", "iw", "hi", "hu", "is", "id", "ga", "it", "ja", "ko",
             "lv", "lt", "mk", "ms", "mt", "no", "fa", "pl", "pt", "ro",
             "ru", "sr", "sk", "sl", "es", "sw", "sv", "th", "tr", "uk",
             "vi", "cy", "yi"]

    def receive(self, puid, action, detail):
        self.target_lang = action
        self.detail = detail

    def _google_translate(self):
        "Translate with google.cloud lib"
        self.logger.log("Translating sentence using google translate api")
        if self.client is None:
            self.client = translate.Client()
        trans = self.client.translate(
            self.detail,
            target_language = self.target_lang
        )
        return trans['translatedText']
