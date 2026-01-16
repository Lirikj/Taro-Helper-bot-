import sqlite3 



def create_baza():
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            real_name TEXT,
            birth_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS premium (
            user_id INTEGER PRIMARY KEY,
            premium_type TEXT,
            premium_status TEXT,
            premium_expiry DATE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spread (
            user_id INTEGER PRIMARY KEY,
            conf_spread TEXT, 
            date TEXT, 
            matrix TEXT, 
            kol_questions INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AD (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT
        )
    ''')

    conn.commit()
    conn.close() 


def update_info(user_id, username, name):
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id FROM conversations WHERE user_id = ?', (user_id,))
    user_exists = cursor.fetchone()
    
    if user_exists:
        cursor.execute('''
            UPDATE conversations 
            SET username = ?, name = ?
            WHERE user_id = ?
        ''', (username if username else '', name, user_id))
        conn.commit()
        updated = True
    else:
        updated = False
    
    conn.close()
    return updated


def user_exists(user_id):
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id FROM conversations WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    return result is not None


def has_premium(user_id):
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT premium_status, premium_expiry FROM premium WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if not result:
        return False
    
    status, expiry = result
    if status == 'active' and expiry:
        from datetime import datetime
        expiry_date = datetime.strptime(expiry, '%Y-%m-%d')
        if expiry_date > datetime.now():
            return True
    return False


def get_user_data(user_id):
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT real_name, birth_date FROM conversations WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return {'real_name': result[0], 'birth_date': result[1]}
    return None


def can_ask_question(user_id):
    from datetime import datetime
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT date, kol_questions FROM spread WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    if not result:
        cursor.execute('INSERT INTO spread (user_id, date, kol_questions) VALUES (?, ?, 0)', (user_id, today))
        conn.commit()
        conn.close()
        return True, 2
    
    saved_date, kol_questions = result
    
    if saved_date != today:
        cursor.execute('UPDATE spread SET date = ?, kol_questions = 0 WHERE user_id = ?', (today, user_id))
        conn.commit()
        conn.close()
        return True, 2
    
    conn.close()
    if kol_questions >= 2:
        return False, 0
    return True, 2 - kol_questions


def increment_question_count(user_id):
    from datetime import datetime
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT date, kol_questions FROM spread WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    if not result:
        cursor.execute('INSERT INTO spread (user_id, date, kol_questions) VALUES (?, ?, 1)', (user_id, today))
    else:
        saved_date, kol_questions = result
        if saved_date != today:
            cursor.execute('UPDATE spread SET date = ?, kol_questions = 1 WHERE user_id = ?', (today, user_id))
        else:
            cursor.execute('UPDATE spread SET kol_questions = kol_questions + 1 WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()


def get_matrix(user_id):
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT matrix FROM spread WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result and result[0]:
        return result[0]
    return None


def save_matrix(user_id, matrix_text):
    from datetime import datetime
    conn = sqlite3.connect('baza.db')
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT user_id FROM spread WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    if not result:
        cursor.execute('INSERT INTO spread (user_id, date, matrix, kol_questions) VALUES (?, ?, ?, 0)', 
                    (user_id, today, matrix_text))
    else:
        cursor.execute('UPDATE spread SET matrix = ? WHERE user_id = ?', (matrix_text, user_id))
    
    conn.commit()
    conn.close()