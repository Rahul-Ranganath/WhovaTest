import sys
import sqlite3

class AgendaLookup:
    DB_NAME = "interview_test.db"

    def __init__(self):
        self.conn = sqlite3.connect(self.DB_NAME)
        self.cursor = self.conn.cursor()

    def lookup_sessions(self, column, value):
        query = f"SELECT * FROM agendas WHERE {column} = ?"
        self.cursor.execute(query, (value,))
        sessions = self.cursor.fetchall()
        print("sessions: ",sessions)
        sub_sessions = []
        for session in sessions:
            if session[4] == "Session":
                #sub_session_query = f"SELECT * FROM agendas WHERE session_type = 'Sub-session' AND session_title = ? AND date = ? AND time_start = ? AND time_end = ?"
                sub_session_query = "SELECT * FROM agendas WHERE session_type = 'Sub-session' AND parent_session_id = ?"
                self.cursor.execute(sub_session_query, (session[0],))
                sub_sessions.extend(self.cursor.fetchall())
                print("sub-sessions: ",sub_sessions)

        sessions.extend(sub_sessions)

        return sessions
        
    def lookup_sessions_by_speaker(self, speaker):
        query = f"SELECT * FROM agendas WHERE speakers LIKE ?"
        self.cursor.execute(query, ('%' + speaker + '%',))
        sessions = self.cursor.fetchall()
        return sessions    

    def print_sessions(self, sessions):
        for session in sessions:
            print("Date:", session[1])
            print("Time Start:", session[2])
            print("Time End:", session[3])
            print("Session Type:", session[4])
            print("Session Title:", session[5])
            print("Location:", session[6])
            print("Description:", session[7])
            print("Speakers:", session[8])
            print("-" * 50)

    def close_connection(self):
        self.conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./lookup_agenda.py column value")
    else:
        column = sys.argv[1]
        value = sys.argv[2]

        valid_columns = ["date", "time_start", "time_end", "session_title", "location", "description", "speakers"]
        if column not in valid_columns:
            print("Invalid column. Please choose from:", ", ".join(valid_columns))
        else:
            lookup_tool = AgendaLookup()
            #sessions = lookup_tool.lookup_sessions(column, value)
            if column == "speakers":
                sessions = lookup_tool.lookup_sessions_by_speaker(value)
            else:
                sessions = lookup_tool.lookup_sessions(column, value)
            lookup_tool.print_sessions(sessions)
            lookup_tool.close_connection()
