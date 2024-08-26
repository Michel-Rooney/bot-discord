import sqlite3


def migrations():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id INTEGER,
            guild_id INTEGER,
            xp INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS study (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user INTEGER,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            total_time INTEGER,
            xp INTEGER,
            channel_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user) REFERENCES user (id)
        )
    ''')

    conn.commit()
    conn.close()


def get_user(member):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    c.execute('SELECT * FROM user WHERE discord_id = ?', (member.id,))
    user = c.fetchone()

    conn.close()
    return user


def get_study_by_user(user_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    c.execute('''
        SELECT * FROM study
        WHERE user = ?
        ORDER BY created_at DESC
        LIMIT 1
    ''', (user_id,))

    study = c.fetchone()

    conn.close()
    return study


def create_user(member, guild_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    c.execute('''
        INSERT INTO user (id_discord, id_guild, xp)
        VALUES (?, ?, ?)
    ''', (member.id, guild_id, 0))

    conn.commit()
    conn.close()
