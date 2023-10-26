import xlrd
from db_table import db_table

# Define the schema for the SQLite database table
agenda_table_schema = {
    "id": "integer PRIMARY KEY",
    "date": "text",
    "time_start": "text",
    "time_end": "text",
    "session_type": "text",
    "session_title": "text",
    "location": "text",
    "description": "text",
    "speakers": "text"
}

def parse_excel(filename):
    workbook = xlrd.open_workbook(filename)
    sheet = workbook.sheet_by_index(0)  # Assuming data is in the first sheet

    agendas = []
    current_session = None

    # Start parsing from row 16
    for row_idx in range(15, sheet.nrows):
        row = sheet.row_values(row_idx)
        # Check if it's a session or sub-session
        session_type = "Session"
        if row[3] == "Sub":
            session_type = "Sub-session"
        # Split speakers by semicolon
        speakers = ";".join(row[7].split(';'))

        # Create agenda dictionary
        agenda = {
            "date": row[0],
            "time_start": row[1],
            "time_end": row[2],
            "session_type": session_type,
            "session_title": row[4],
            "location": row[5],
            "description": row[6],
            "speakers": speakers
        }

        # If it's a session, update current session
        if session_type == "Session":
            current_session = agenda
            agendas.append(current_session)
        else:
            # If it's a sub-session, add it under the current session
            if current_session:
                current_session.setdefault("sub_sessions", []).append(agenda)

    return agendas

def import_agenda_to_db(agendas):
    # Initialize the database table
    agenda_table = db_table("agendas", agenda_table_schema)

    for agenda in agendas:
        # Insert session into the database
        session_id = agenda_table.insert({
            "date": agenda["date"],
            "time_start": agenda["time_start"],
            "time_end": agenda["time_end"],
            "session_type": agenda["session_type"],
            "session_title": agenda["session_title"],
            "location": agenda["location"],
            "description": agenda["description"],
            "speakers": agenda["speakers"]
        })

        # Insert sub-sessions under the session
        if "sub_sessions" in agenda:
            for sub_session in agenda["sub_sessions"]:
                agenda_table.insert({
                    "date": sub_session["date"],
                    "time_start": sub_session["time_start"],
                    "time_end": sub_session["time_end"],
                    "session_type": sub_session["session_type"],
                    "session_title": sub_session["session_title"],
                    "location": sub_session["location"],
                    "description": sub_session["description"],
                    "speakers": sub_session["speakers"]
                })
    
    # Testing if data is inserted
    print("Data in the database:")
    rows = agenda_table.select_all()
    for row in rows:
        print(row)
    # Close the database connection
    agenda_table.close()

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: ./import_agenda.py agenda.xls")
    else:
        filename = sys.argv[1]
        agendas = parse_excel(filename)
        import_agenda_to_db(agendas)
        print("Agenda imported successfully.")
