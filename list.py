#!/usr/bin/env python3
""" Simple command line tool to keep track of periodic things.
Returns for example:
Item            Period     Last renewed     Planned           Days left
1. Toothbrush   3 months   July 4th, 2018   October 4th, 2018 30
2. Hairdresser  6 weeks    June 6th, 208    July 20th, 2018   -20
Overdue:
2. Hairdresser!

Accepts commands such as:
    Create new entry
        list.py --new
        Enter item name:
        Period in days/weeks/months/years:
        Last renewed (dd/mm/yy):
    Update entry with index 3
        list.py --update 3
    Delete entry with index 2
        list.py --delete 2

Extend with Gmail and Google calendar integration?
"""
import sys, os

import argparse
import sqlite3
from datetime import datetime, timedelta, date
from tabulate import tabulate

def connect_database(database_path):
    conn = sqlite3.connect(database_path)
    print("Opened connection.")
    conn.execute('''CREATE table IF NOT EXISTS list
             (id INTEGER,
              name TEXT,
              period TEXT,
              last DATE,
              plan DATE,
              daysleft INTEGER
             );''')
    conn.commit()
    return conn

def update_database(conn):
    cursor = conn.cursor()
    idsDB = cursor.execute('''SELECT id FROM list;''')
    ids = idsDB.fetchall()

    for id in ids:
        id = int(id[0])
        planned = cursor.execute('''SELECT plan FROM list WHERE id=(?);''', (id,))
        planned = planned.fetchone()[0]
        planned = datetime.strptime(planned, '%Y-%m-%d')
        planned = planned.date()
        daysleft = int((planned - date.today()).days)
        conn.execute('''UPDATE list SET daysleft=(?) WHERE id=(?);''',
                        (daysleft, id))
        conn.commit()
    return

def show_list(conn):
    update_database(conn)
    cursor = conn.execute('''SELECT * FROM list;''')
    headers = ['Id', 'Item', 'Period', 'Last renewed', 'Planned', 'Days Left']
    table_content = []
    for row in cursor:
        row_content = [row[0], row[1], row[2], row[3], row[4], row[5]]
        table_content.append(row_content)

    print(tabulate(table_content, headers, tablefmt='plain'))

def add_item(conn):
    itemname = input("Enter item name: ")
    period = int(input("Period in days: "))
    lastrenewed = datetime.strptime(input("Last renewed (dd-mm-yy): "), '%d-%m-%y')
    lastrenewed = lastrenewed.date()
    planned = lastrenewed + timedelta(days=period)
    daysleft = int((planned - date.today()).days)

    cursor = conn.cursor()
    ids = cursor.execute('''SELECT MAX(id) FROM list;''')
    max_id = ids.fetchall()

    if (max_id[0])[0] == None:
        new_id = 1
    else:
        new_id = (max_id[0])[0] + 1

    conn.execute('''INSERT INTO list VALUES (?, ?, ?, ?, ?, ?);''',
            (new_id, itemname, period, lastrenewed, planned, daysleft))
    conn.commit()
    return

def delete_item(conn):
    del_id = input("Item to delete: ")

    for entry in item_exist(conn, del_id):
        existance = entry[0]
    if existance:
        conn.execute('''DELETE FROM list WHERE id = (?);''', (del_id))
        conn.commit()
    else:
        print("Item does not exist.")
    return

def update_item(conn):
    update_id = input("Item to update: ")
    update_date = datetime.strptime(input("Last renewed (dd-mm-yy): "), '%d-%m-%y')
    update_date = update_date.date()

    for entry in item_exist(conn, update_id):
        existance = entry[0]
    if existance:
        cursor = conn.cursor()
        periodDB = cursor.execute('''SELECT period FROM list WHERE id = (?);''',
                                  (update_id))
        for entry in periodDB:
            period = int(entry[0])
        update_plan_date = update_date + timedelta(days=period)

        conn.execute('''UPDATE list SET last = (?) WHERE id = (?);''',
                        (update_date, update_id))
        conn.execute('''UPDATE list SET plan = (?) WHERE id = (?);''',
                        (update_plan_date, update_id))
        conn.commit()
    else:
        print("Item does not exist.")
    return

def item_exist(conn, id):
    """ Check if item exists before trying to update or delete """
    cursor = conn.cursor()
    existance = cursor.execute('''SELECT COUNT(1) FROM list WHERE id=(?);''', (id))
    return existance

def clear_console():
    print("\033[H\033[J")

def send_help():
    print('Commands: \n s - Show list \n a - Add item \n u - Update item \n' +
    ' d - Delete item \n q - Quit program \n c - Clear console and show list \n')

def action_tree(conn):
    action_trigger = 1
    while action_trigger:
        action = input("Input action [s/a/u/d/q]: ")
        if action == 'a':
            add_item(conn)
            action_trigger = more_actions(conn)
        elif action == 'u':
            update_item(conn)
            action_trigger = more_actions(conn)
        elif action == 'd':
            delete_item(conn)
            action_trigger = more_actions(conn)
        elif action == 's':
            show_list(conn)
        elif action == 'q':
            action_trigger = 0
        elif action == 'c':
            clear_console()
            show_list(conn)
        elif action == 'help':
            send_help()
            show_list(conn)
        else:
            print("Unknown action.")
            action_trigger = 1
    return

def more_actions(conn):
    choice = input("More actions? [y/n] ")
    if choice == 'y':
        action_trigger = 1
    elif choice == 'n':
        action_trigger = 0
    else:
        print("Unknown response; assumed no.")
        action_trigger = 0
    return action_trigger

def run(args):
    pathname = os.path.dirname(sys.argv[0])
    if len(pathname) == 0:
        # Command was 'python3 list.py'
        database_path = 'periodiclist.db'
    else:
        # Command was 'python3 ./list.py' or './list.py'
        database_path = pathname + '/periodiclist.db'

    conn = connect_database(database_path)
    update_database(conn)

    if args.additem:
        add_item(conn)
    elif args.update:
        update_item(conn)
    elif args.delitem:
        delete_item(conn)
    else:
        show_list(conn)

    action_tree(conn)
    conn.close()
    print("Closed connection.")

def main():
    parser = argparse.ArgumentParser(description="Keep track of periodic things.")
    # Show list
    # parser.add_argument("-s", "--show", dest="showlist", action="store_true")
    # Add entry
    parser.add_argument("-a", "--add", dest="additem", action="store_true")
    # Update entry
    parser.add_argument("-u", "--update", dest="update", action="store_true")
    # Delete entry
    parser.add_argument("-d", "--del", dest="delitem", action="store_true")

    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)
    input()

if __name__ == "__main__":
    main()
