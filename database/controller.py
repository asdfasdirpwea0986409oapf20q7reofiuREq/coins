import sqlite3

def connect():
    connection = sqlite3.connect("database\\database.db", check_same_thread = False)
    try:
        connection.execute("""CREATE TABLE members (
    id integer PRIMARY KEY AUTOINCREMENT,
    username text,
    email text,
    pfp text,
    coins integer
);""")
    except sqlite3.OperationalError:
        pass
    return connection

def create(connection, id, username, pfp, email, coins):
    while True:
        try:
            connection.execute(f"INSERT INTO members (id, username, email, pfp, coins) VALUES ('{id}', '{username}', '{email}', '{pfp}', '{coins}');")
            connection.commit()
            break
        except sqlite3.IntegrityError:
            id += 1
            continue

def retrieve(connection):
    cursor = connection.execute(f"SELECT * FROM members;")
    output = []
    for row in cursor:
        entry = {}
        entry["id"] = row[0]
        entry["username"] = row[1]
        entry["email"] = row[2]
        entry["pfp"] = row[3]
        entry["coins"] = row[4]
        output.append(entry)
    return output

def update(connection, id, column, new):
    connection.execute(f"UPDATE members SET {column} = '{new}' WHERE ID = '{id}';")
    connection.commit()

def delete(connection, id):
    connection.execute(f"DELETE FROM members WHERE id = '{id}'")
    connection.commit()

#update(connect(), 0, "coins", 9999999999)
#delete(connect(), 0)