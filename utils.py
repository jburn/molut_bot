import sqlite3
import logging
from constants import *
from random import choice as random_choice
        

def init_db():
    """Check if db has been initialized. If not, initialize it"""
    db_con = sqlite3.connect(DB_PATH)
    cur = db_con.cursor()
    res = cur.execute("SELECT name FROM sqlite_master")
    if res.fetchone() is None:
        db_con.cursor().execute("CREATE TABLE mokous(id, paikka, mindeksi)")
        db_con.commit()
        logging.info("Mokous database created")

def insert_to_db(place: str, mindeksi: str):
    """Insert mokous data into database

    Args:
        place (str): where the mokous took place
        mindeksi (str): mindex in this occasion

    Returns:
        bool: True if successful, False if unsuccessful
    """    
    if not ((isfloat(mindeksi)) and (sql_input_ok(place))):
        logging.warning(f"invalid or suspicious input: {place} {mindeksi}")
        return False
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    res = cur.execute("SELECT COUNT(ALL) FROM mokous")
    count = res.fetchone()[0]
    cur.execute(f"""
        INSERT INTO mokous VALUES 
            ({count}, '{place.lower().strip()}', {mindeksi.lower().strip()})
    """)
    con.commit()
    logging.info(f"saved mokous ({count}, {place.lower().strip()}, {mindeksi.lower().strip()})")
    return True

def get_from_db():
    """Return all mokous data from database

    Returns:
        list: all mokous data from database
    """
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()    
    res = cur.execute("""
    SELECT * FROM mokous
    """)
    mokouslist = res.fetchall()
    return mokouslist

def get_filedata(path: str):
    """get all data from file

    Args:
        path (str): path to file

    Returns:
        string: file data as a string
    """
    try:
        with open(path, 'r') as rfile:
            data = rfile.read()
        logging.info(f"File {path} read successfully")
    except:
        logging.error(f"ERROR: No file found in {path}")
        return
    return data

def drink_command(key: str):
    """Random drink creator for for the drink command

    Args:
        key (str): what kind of drink we are creating

    Returns:
        str: created drink (or error message)
    """    
    if key == "mieto":
        maito = random_choice(MAITO)
        mieto = random_choice(MIEDOT)
        msg = f"{maito} + {mieto.strip()}\n= {maito[0] + mieto[1:]}"
    elif key == "kova":
        maito = random_choice(MAITO)
        kova = random_choice(KOVAT)
        msg = f"{maito} + {kova}\n= {maito[0] + kova[1:]}"
    elif key == "macktail":
        maito = random_choice(MAITO)
        mieto = random_choice(MIEDOT)
        kova = random_choice(KOVAT)
        msg = f"{maito} + {mieto.strip()} + {kova}\n= {maito[0] + mieto[1] + kova[2:]}"
    else:
        logging.error(f"invalid juoma button callback data: {key}")
        msg = "Fatal backend error :D"
    return msg

def isfloat(num: str):
    """Check if string is a viable float

    Args:
        num (float, int): number to check

    Returns:
        bool: if string is a viable float
    """    
    try:
        float(num)
        return True
    except ValueError:
        return False

def sql_input_ok(string: str):
    """Check for suspicious sql statements 

    Args:
        string (string): target for analysis

    Returns:
        boolean: true if nothing sus found, false if string is sus
    """    
    string = string.lower()
    suspicious_str = [
        "--",
        "union",
        "delete",
        "create",
        "drop",
        "update",
        "select",
        "alter",
        "insert",
        ";"
    ]
    if string == "":
        return False
    if string[0] == ".":
        return False
    for sus in suspicious_str:
        if sus in string:
            return False
    return True
