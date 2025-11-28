import csv
import os
import sys

class Localization:
    def __init__(self):
        self.data = {}
        self.current_lang = 'en'
        self.load_data()
        
    def load_data(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
        path = os.path.join(base_path, 'assets', 'data', 'strings.csv')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.data[row['key']] = row
        except Exception as e:
            print(f"Failed to load localization: {e}")

    def get(self, key):
        if key in self.data:
            return self.data[key].get(self.current_lang, key)
        return key

    def set_language(self, lang):
        if lang in ['en', 'es']:
            self.current_lang = lang
