import json
from os import getenv

from dotenv import load_dotenv
from telebot import types
import requests
import logging
from transformers import AutoTokenizer

logging.basicConfig(filename='logs.log', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()


class IOP:
    bot_api = str(getenv('BOT_TOKEN'))

    
class GPT:
    def __init__(self, system_content=""):
        self.system_content = system_content
        self.URL = "http://158.160.135.104:1234/v1/chat/completions"
        self.HEADERS = {"Content-Type": "application/json"}
        self.MAX_TOKENS = 50
        self.assistant_content = "Решим задачу по шагам: "

    @staticmethod
    def count_tokens(prompt):
        tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")  
        return len(tokenizer.encode(prompt))

    def process_resp(self, response) -> [bool, str]:  # type: ignore
        if response.status_code < 200 or response.status_code >= 300:
            self.clear_history()
            error_msg = f"Ошибка: {response.status_code}"
            logger.error(error_msg)
            return False, error_msg

        try:
            full_response = response.json()
        except:
            self.clear_history()
            return False, "Ошибка получения JSON"

        if "error" in full_response or 'choices' not in full_response:
            self.clear_history()
            return False, f"Ошибка: {full_response}"

        result = full_response['choices'][0]['message']['content']

        if not result:
            self.clear_history()
            return True, 'Объяснение закончено!'

        self.save_history(result)
        return True, self.assistant_content

    def make_promt(self, user_request):
        json = {
            "messages": [
                {"role": "system", "content": self.system_content},
                {"role": "user", "content": user_request},
                {"role": "assistant", "content": self.assistant_content},
            ],
            "temperature": 1.2,
            "max_tokens": self.MAX_TOKENS,
        }
        return json

    def send_request(self, json):
        resp = requests.post(url=self.URL, headers=self.HEADERS, json=json)
        return resp

    def save_history(self, content_response):
        self.assistant_content = self.assistant_content + content_response + ' '

    def clear_history(self):
        self.assistant_content = "Решим задачу по шагам: "