# session_manager.py

import json
import os

class SessionManager:
    def __init__(self, filename='sessions.json'):
        self.filename = filename
        self.sessions = self.load_sessions()

    def load_sessions(self):
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, 'r') as file:
            return json.load(file).get('sessions', [])

    def save_sessions(self):
        with open(self.filename, 'w') as file:
            json.dump({'sessions': self.sessions}, file, indent=4)

    def add_session(self, session_string):
        if session_string not in self.sessions:
            self.sessions.append(session_string)
            self.save_sessions()
            return True
        return False

    def remove_session(self, session_string):
        if session_string in self.sessions:
            self.sessions.remove(session_string)
            self.save_sessions()
            return True
        return False

    def get_all_sessions(self):
        return self.sessions
