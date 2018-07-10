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

Store as SQL database? Good excersise even if it is way way way overkill.
Extend with Gmail and Google calendar integration
"""
import argparse
import sqlite3
from datetime import datetime, timedelta, date

def connect_database():
    conn = sqlite3.connect('periodiclist.db')
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

def show_list(conn):
    cursor = conn.execute('''SELECT * FROM list;''')
    print("Id Item \t Period \t Last renewed \t Planned \t" +
            "Days Left \n")
    for row in cursor:
        lastrenewed = row[3].strftime('%d-%m-%y')
        planned = row[4].strftime('%d-%m-%y')
        print("%d %s \t %s \t %s \t %s \t %d \n" % (row[0], row[1], row[2],
                lastrenewed, planned, row[5]))

def add_item(conn):
    itemname = input("Enter item name: ")
    period = int(input("Period in days: "))
    lastrenewed = datetime.strptime(input("Last renewed (dd-mm-yy): "), '%d-%m-%y')
    planned = lastrenewed.date() + timedelta(days=period)
    daysleft = int((planned - date.today()).days)
    print(daysleft)
    conn.execute('''INSERT INTO list VALUES (?, ?, ?, ?, ?, ?);''',
            (1, itemname, period, lastrenewed, planned, daysleft))
    conn.commit()
    #        Enter item name:
    #        Period in days/weeks/months/years:
    #        Last renewed (dd/mm/yy):
    # Assign lowest ID still available
    return

def delete_item(conn):
    # Which item do you want to delete?
    # Does that item_exist()?
    # if yes, delete, if no exit
    return

def update_item(conn):
    # Which item do you want to update?
    # Does that item_exist()?
    # if no, exit
    # Update today?
    # If no, what date?
    # Update
    return

def item_exist(conn, id):
    # Check database if id exists
    return existance

def run(args):
    conn = connect_database()
        # Calculate days left
        # Update database

    if args.showlist:
        show_list(conn)
    elif args.additem:
        add_item(conn)
    elif args.update:
        update_item(conn)
    elif args.delitem:
        delete_item(conn)

    conn.close()
    print("Closed connection.")

def main():
    parser = argparse.ArgumentParser(description="Keep track of periodic things.")
    # Create new database
    # parser.add_argument("-c", "--credb", dest="createdb", action="store_true")
    # Show list
    parser.add_argument("-s", "--show", dest="showlist", action="store_true")
    # Add entry
    parser.add_argument("-a", "--add", dest="additem", action="store_true")
    # Update entry
    parser.add_argument("-u", "--update", dest="update", action="store_true")
    # Delete entry
    parser.add_argument("-d", "--del", dest="delitem", action="store_true")

    # parser.add_argument("-z", dest="zaak", type=str, required=False)

    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
