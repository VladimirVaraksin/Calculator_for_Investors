# This file is part of the "Calculator for Investors" project.

from db import (connect_db, create_table_companies, create_table_financials,
                insert_company, insert_financials, select_all_companies, create_company, create_financial, select_company, select_financial, update_financial, delete_company)
import sqlite3

def get_main_menu():
    return ['0', '1', '2'], "\nMAIN MENU\n0 Exit\n1 CRUD operations\n2 Show top ten companies by criteria\nEnter an option:\n\n"

def get_crud_menu():
    return (
        ['0', '1', '2', '3', '4', '5'],
        "\nCRUD MENU\n0 Back\n1 Create a company\n2 Read a company\n3 Update a company\n4 Delete a company\n5 List all companies\nEnter an option:\n\n"
    )

def get_top_ten_menu():
    return (
        ['0', '1', '2', '3'],
        "\nTOP TEN MENU\n0 Back\n1 List by ND/EBITDA\n2 List by ROE\n3 List by ROA\nEnter an option:\n\n"
    )

def get_menu_choice(valid_choices, prompt, menu_type=None):
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print("Invalid option!")
        if menu_type is not None and menu_type == 'TOP TEN':
            return None

def get_company_input(create_new: bool = True) -> dict:
    def get_input(prompt, cast_func=str):
        while True:
            value = input(prompt).strip()
            if value == '':
                print("Input can not be empty!")
                continue
            try:
                return cast_func(value)
            except ValueError:
                print("False format! Please try again.")

    fields_create = [
        ('ticker', "Enter ticker (in the format 'MOON'):\n> ", str),
        ('name', "Enter company (in the format 'Moon Corp'):\n> ", str),
        ('sector', "Enter industries (in the format 'Technology'):\n> ", str),
        ('ebitda', "Enter ebitda (in the format '987654321'):\n> ", float),
        ('sales', "Enter sales (in the format '987654321'):\n> ", float),
        ('net_profit', "Enter net profit (in the format '987654321'):\n> ", float),
        ('market_price', "Enter market price (in the format '987654321'):\n> ", float),
        ('net_debt', "Enter net debt (in the format '987654321'):\n> ", float),
        ('assets', "Enter assets (in the format '987654321'):\n> ", float),
        ('equity', "Enter equity (in the format '987654321'):\n> ", float),
        ('cash_equivalents', "Enter cash equivalents (in the format '987654321'):\n> ", float),
        ('liabilities', "Enter liabilities (in the format '987654321'):\n> ", float)
    ]
    fields_update = fields_create[3:]  # Nur Finanzfelder

    fields = fields_create if create_new else fields_update
    return {key: get_input(prompt, cast_func) for key, prompt, cast_func in fields}

def list_matching_companies(companies: list) -> None:
    """Prints the list of companies that match the search criteria."""
    if not companies:
        print("Company not found!")
    else:
        for i, company in enumerate(companies):
            print(f"{i} {company[1]}")

def calculate_ratios(financials: tuple) -> dict:
    """Calculates financial ratios from the financial data."""
    ebitda, sales, net_profit, market_price, net_debt, assets, equity, cash_equivalents, liabilities = financials[1:]
    return {
        'P/E': market_price / net_profit if market_price and net_profit else None,
        'P/S': (market_price / sales) if market_price and sales else None,
        'P/B': market_price / assets if assets and market_price else None,
        'ND/EBITDA': (net_debt / ebitda) if ebitda and net_debt else None,
        'ROE': (net_profit / equity) if equity and net_profit else None,
        'ROA': (net_profit / assets) if assets and net_profit else None,
        'L/A': (liabilities / assets) if assets and liabilities else None
    }

def print_financial_ratios(ratios: dict) -> None:
    """Prints the financial ratios in a formatted way."""
    for key, value in ratios.items():
        if value is not None:
            print(f"{key} = {value:.2f}")
        else:
            print(f"{key} = None")

def get_company_by_name(con: sqlite3.Connection) -> tuple | None:
    """Prompts the user to enter a company name and returns the company data."""
    name = input("Enter company name:\n").strip()
    companies = select_company(con, name)
    list_matching_companies(companies)
    if companies:
        number = input("Enter company number:\n").strip()
        if number.isdigit() and 0 <= int(number) < len(companies):
            return companies[int(number)]
        else:
            print("Invalid company number!")
            return None
    return None

def get_top_companies_by_ratio(con: sqlite3.Connection, companies: list[tuple], ratio: str) -> list[dict]:
    """Gibt die Top-10-Unternehmen nach dem angegebenen Verhältnis zurück."""
    result = []
    for company in companies:
        ticker = company[0]
        financials = select_financial(con, ticker)
        if financials:
            ratios = calculate_ratios(financials)
            value = ratios.get(ratio)
            if value is not None:
                result.append({'ticker': ticker, 'ratio': value})
    sorted_companies = sorted(result, key=lambda c: c['ratio'], reverse=True)
    return sorted_companies[:10]

def format_ratio(value):
    rounded = round(value, 2)
    return f"{rounded:.2f}".rstrip('0').rstrip('.')

def print_top_companies(companies):
    for company in companies:
        ratio_str = format_ratio(company['ratio'])
        print(f"{company['ticker']} {ratio_str}")

def crud_operations(con: sqlite3.Connection, choice: str):
    match choice:
        case '0':
            return  # Back to the main menu
        case '1':
            company = get_company_input()
            create_company(con, company['ticker'], company['name'], company['sector'])
            create_financial(con, company['ticker'], company['ebitda'], company['sales'], company['net_profit'],
                             company['market_price'], company['net_debt'], company['assets'], company['equity'],
                             company['cash_equivalents'], company['liabilities'])
            print("Company created successfully!")
        case '2':
            company = get_company_by_name(con)
            if company:
                print(f"{company[0]} {company[1]}")
                financials = select_financial(con, company[0])
                ratios = calculate_ratios(financials)
                print_financial_ratios(ratios)
        case '3':
            company = get_company_by_name(con)
            if company:
                updated_company = get_company_input(create_new=False)
                update_financial(con, company[0], updated_company['ebitda'], updated_company['sales'], updated_company['net_profit'], updated_company['market_price'], updated_company['net_debt'], updated_company['assets'], updated_company['equity'], updated_company['cash_equivalents'], updated_company['liabilities'])
                print("Company updated successfully!")
        case '4':
            company = get_company_by_name(con)
            if company:
                delete_company(con, company[0])
                print("Company deleted successfully!")
        case '5':
            print("COMPANY LIST")
            company_list = select_all_companies(con)
            for company in company_list:
                print(f"{company[0]} {company[1]} {company[2]}")
        case _:
            print("Invalid option!")

def main(con: sqlite3.Connection):
    print("Welcome to the Investor Program!")
    while True:
        menu = get_main_menu()
        choice = get_menu_choice(menu[0], menu[1])
        match choice:
            case '0':
                print("Have a nice day!")
                break
            case '1':
                sub_menu = get_crud_menu()
                choice = get_menu_choice(sub_menu[0], sub_menu[1])
                crud_operations(con, choice)
            case '2':
                sub_menu = get_top_ten_menu()
                choice = get_menu_choice(sub_menu[0], sub_menu[1], menu_type='TOP TEN')
                if choice is None or choice == '0':
                    continue
                companies = select_all_companies(con)
                if not companies:
                    print("No companies found!")
                    continue
                ratios = ['ND/EBITDA', 'ROE', 'ROA']
                ratio = ratios[int(choice) - 1]
                top_companies = get_top_companies_by_ratio(con, companies, ratio)
                if top_companies:
                    print(f"TICKER {ratio}")
                    print_top_companies(top_companies)
            case _:
                print("Invalid option!")

if __name__ == "__main__":
    try:
        with connect_db() as connection:
            exists_companies = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='companies';").fetchone()
            exists_financials = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='financial';").fetchone()
            if not exists_companies:
                create_table_companies(connection)
                insert_company(connection, 'data/companies.csv')
            if not exists_financials:
                create_table_financials(connection)
                insert_financials(connection, 'data/financial.csv')
            main(connection)
    except sqlite3.Error as e:
        print(f"There was a database error: {e}")