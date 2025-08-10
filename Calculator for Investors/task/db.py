import sqlite3
import csv

def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect('investor.db')

def create_table_companies(con: sqlite3.Connection):
    """Create the company table if it does not exist."""
    with con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                ticker TEXT PRIMARY KEY,
                name TEXT,
                sector TEXT
            );
        ''')

def create_table_financials(con: sqlite3.Connection):
    """Erstellt die Tabelle financials, falls sie nicht existiert."""
    with con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS financial (
                ticker TEXT PRIMARY KEY,
                ebitda REAL,
                sales REAL,
                net_profit REAL,
                market_price REAL,
                net_debt REAL,
                assets REAL,
                equity REAL,
                cash_equivalents REAL,
                liabilities REAL
            );
        ''')


def insert_company(con: sqlite3.Connection, filename: str):
    """Fügt Firmendaten ein, ignoriert doppelte Ticker."""
    with open(filename, 'r') as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            with con:
                con.execute('''
                    INSERT OR IGNORE INTO companies (ticker, name, sector)
                    VALUES (?, ?, ?);
                ''', (row['ticker'], row['name'], row['sector']))

def to_float(value):
    return float(value) if value.strip() != '' else None

def insert_financials(con: sqlite3.Connection, filename: str):
    """Fügt Finanzdaten in die Tabelle financial ein, behandelt leere Felder."""
    with open(filename, 'r') as file:
        reader = csv.DictReader(file, delimiter=',')
        for row in reader:
            with con:
                con.execute('''
                    INSERT OR IGNORE INTO financial (ticker, ebitda, sales, net_profit, market_price,
                                            net_debt, assets, equity, cash_equivalents, liabilities)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                ''', (
                    row['ticker'],
                    to_float(row['ebitda']),
                    to_float(row['sales']),
                    to_float(row['net_profit']),
                    to_float(row['market_price']),
                    to_float(row['net_debt']),
                    to_float(row['assets']),
                    to_float(row['equity']),
                    to_float(row['cash_equivalents']),
                    to_float(row['liabilities'])
                ))

def select_all_companies(con: sqlite3.Connection):
    """Selects all companies from the database."""
    with con:
        return con.execute('SELECT * FROM companies ORDER BY ticker;').fetchall()

def create_company(con: sqlite3.Connection, ticker: str, name: str, sector: str):
    """Creates a new company in the database."""
    with con:
        con.execute('''
            INSERT OR IGNORE INTO companies (ticker, name, sector)
            VALUES (?, ?, ?);
        ''', (ticker, name, sector))

def create_financial(con: sqlite3.Connection, ticker: str, ebitda: float, sales: float,
                        net_profit: float, market_price: float, net_debt: float,
                        assets: float, equity: float, cash_equivalents: float, liabilities: float):
    """Creates a new financial record in the database."""
    with con:
        con.execute('''
            INSERT OR IGNORE INTO financial (ticker, ebitda, sales, net_profit, market_price,
                                            net_debt, assets, equity, cash_equivalents, liabilities)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (ticker, ebitda, sales, net_profit, market_price,
              net_debt, assets, equity, cash_equivalents, liabilities))

def select_company(con: sqlite3.Connection, name: str) -> list:
    """Wählt Unternehmen anhand des Namens (case-insensitive, LIKE-Suche) aus."""
    with con:
        pattern = f"%{name.lower()}%"
        return con.execute(
            "SELECT * FROM companies WHERE lower(name) LIKE ?;",
            (pattern,)
        ).fetchall()

def select_financial(con: sqlite3.Connection, ticker: str):
    """Wählt Finanzdaten für ein bestimmtes Unternehmen anhand des Tickers aus."""
    with con:
        return con.execute(
            "SELECT * FROM financial WHERE ticker = ?;",
            (ticker,)
        ).fetchone()

def update_financial(con: sqlite3.Connection, ticker: str, ebitda: float, sales: float,
                        net_profit: float, market_price: float, net_debt: float,
                        assets: float, equity: float, cash_equivalents: float, liabilities: float):
    """Aktualisiert Finanzdaten für ein bestimmtes Unternehmen."""
    with con:
        con.execute('''
            UPDATE financial
            SET ebitda = ?, sales = ?, net_profit = ?, market_price = ?,
                net_debt = ?, assets = ?, equity = ?, cash_equivalents = ?, liabilities = ?
            WHERE ticker = ?;
        ''', (ebitda, sales, net_profit, market_price,
              net_debt, assets, equity, cash_equivalents, liabilities, ticker))

def delete_company(con: sqlite3.Connection, ticker: str):
    """Deletes a company and its financial data from the database."""
    with con:
        con.execute('DELETE FROM companies WHERE ticker = ?;', (ticker,))
        con.execute('DELETE FROM financial WHERE ticker = ?;', (ticker,))