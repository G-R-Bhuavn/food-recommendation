import pandas as pd
import sqlite3
from tabulate import tabulate

path_foodData ='C:/Users/GR BHUVAN/Downloads/indian_food.csv'
food_file = pd.read_csv(path_foodData)

def create_connection(food_file):
    conn = None
    try:
        conn = sqlite3.connect(food_file)
        conn.execute('PRAGMA foreign_keys = ON;')  # Enable foreign key constraints
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_food_info_table(conn):
    """Create a table for food information."""
    try:
         cursor = conn.cursor()
         cursor.execute(''' CREATE TABLE IF NOT EXISTS Food_Database (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   foodName TEXT NOT NULL,
                   foodDiet TEXT NOT NULL,
                   flavor TEXT ,
                   region TEXT,
                   course TEXT)''')
         

         cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        userName TEXT NOT NULL
         )''')

         cursor.execute('''CREATE TABLE IF NOT EXISTS goto_food(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        foodDiet TEXT NOT NULL,
                        flavor TEXT ,
                        region TEXT,
                        course TEXT,
                        userId INTEGER,
                        FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE
         )''')

    except sqlite3.Error as e:
         print(e)

def delete_duplicates(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM Food_Database WHERE rowid NOT IN (SELECT MIN(rowid) FROM Food_Database GROUP BY foodName)''')
    except sqlite3.Error as e:
        print(e)

def delete(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''DROP TABLE goto_food''')
        cursor.execute('''DROP TABLE users''')
        print('all data deleted')
    except sqlite3.Error as e:
        print(e)

def reset_user_ids(conn):
    cursor = conn.cursor()
    
    # Retrieve all users and their data
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    
    # Start a new transaction
    #conn.execute("BEGIN TRANSACTION")
    
    try:
        # Delete all entries
        cursor.execute('DELETE FROM users')
        cursor.execute('DELETE FROM sqlite_sequence WHERE name = "users"')
        conn.commit()
        
        # Reinsert users with new IDs
        for user in users:
            cursor.execute('INSERT INTO users (userName) VALUES (?)', (user[1],))
        
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error during resetting user IDs: {e}")

def add_course_column(conn):
    '''Add a course column to the existing table'''
    try:
        cursor = conn.cursor()
        cursor.execute('ALTER TABLE Food_Database ADD COLUMN course TEXT')
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def insert_food_data(conn, food_file):
    '''Insert infos into the table'''
    try:
        cursor = conn.cursor()
        for index, row in food_file.iterrows():
            foodName = row['name']
            foodDiet = row['diet']
            flavor = row['flavor_profile']
            region = row['region']
            course = row['course']

            # Check if the record already exists
            cursor.execute('''
                SELECT COUNT(*)
                FROM Food_Database
                WHERE foodName = ? AND foodDiet = ? AND flavor = ? AND region = ? AND (course = ? OR course IS NULL)
            ''', (foodName, foodDiet, flavor, region, course))
            
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO Food_Database (foodName, foodDiet, flavor, region, course)
                    VALUES (?, ?, ?, ?, ?)
                ''', (foodName, foodDiet, flavor, region, course))

        conn.commit()
    except sqlite3.Error as e:
        print(e)

def print_Table(conn):
    '''Printing all the values of the created table '''
    try:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM Food_Database''')
        column_names = [description[0] for description in cursor.description]
        #print('\t'.join(column_names))
        rows = cursor.fetchall()
        # for row in rows:
        #     print('\t'.join(map(str,row)))
        print(tabulate(rows, headers=column_names, tablefmt="pretty"))
    except sqlite3.Error as e:
        print(e)

def distinct_values(conn,column):
    '''Retrieve distinct values from a specified column'''
    cursor = conn.cursor()
    query = f"SELECT DISTINCT {column} FROM Food_Database"
    cursor.execute(query)
    values = cursor.fetchall()

    # Convert list of tuples to a flat list
    distinct_values = [val[0] for val in values if val[0] is not None]

    # Print in table format using tabulate
    table = [[value] for value in distinct_values]
    print (tabulate(table, headers=[column.capitalize()], tablefmt="pretty"))

def food_selection(conn):

    '''flavour selection'''
    distinct_values(conn,'flavor')
    flavour = input("Enter flavor of preference , if no prefernce type 'all':\n").strip().lower()

    '''Diet selection'''
    distinct_values(conn,'foodDiet')
    diet = input("Enter your preference of region, if no preference type 'all':\n").strip().lower()

    '''Region selection'''
    distinct_values(conn,'region')
    region = input("Enter your prefered region , if no prefernce type 'all'\n").strip().lower()

    '''Course selection'''
    distinct_values(conn,'course')
    course = input("Enter your prefered course , if no prefernce type 'all'\n").strip().lower()

    return flavour, diet, region, course

def goto_insert_data(conn):
    try:
        cursor = conn.cursor()
        # user data 
        usr = input("Enter the name of the user:\n ")
        cursor.execute('''INSERT INTO  users(userName) VALUES(?)''',(usr,))
        # getting info of newly updated userid
        user_id = cursor.lastrowid
        # goto data
        flavour , diet, region, course = food_selection(conn)
        cursor.execute('''INSERT INTO goto_food(userId,foodDiet,flavor,region,course) VALUES (? ,?, ?, ?, ?)''',(user_id,flavour,diet,region,course))
        conn.commit()
    except sqlite3.Error as e:
        print(e) 

def goto_preferences_functions(conn):

    try:
        cursor = conn.cursor()
        sel = input("Enter your choice\n1.Order from goto\n2.Update goto info\nEnter the number as your choice:\n")
        match (sel):
            case '1':
                 # Check if goto_food table is empty
                cursor.execute('''SELECT COUNT(*) FROM goto_food''')
                count = cursor.fetchone()[0]
                if count == 0:
                    print("Table empty\n")
                    goto_insert_data(conn)
                 
                # getting user names   
                cursor.execute('''SELECT * FROM users''')
                column_names = [description[0] for description in cursor.description]
                users = cursor.fetchall()
                print(tabulate(users,headers=column_names, tablefmt="pretty"))
                # selecting your choice
                choice = input("Enter the number corresponding to your user choice:\n")
                user_id = users[int(choice) - 1][0]  # Get the user ID based on choice
                # getting needed values based on userid
                cursor.execute('''SELECT * FROM goto_food WHERE userId = ?''',(user_id,))
                column_names = [description[0] for description in cursor.description]
                values = cursor.fetchall()
                print(tabulate(values,headers=column_names,tablefmt="pretty"))
                if values:
                       food_preferences = values[0]
                       # Corrected the order of columns to: id, flavor,foodDiet, region, course, userId
                       id, flavor,diet, region, course, user_id = food_preferences
                       print(f"Using preferences: Diet={diet}, Flavor={flavor}, Region={region}, Course={course}")

                        # Build the query dynamically based on preferences
                       query = '''SELECT DISTINCT foodName FROM Food_Database WHERE 1=1'''
                       params = []

                       if diet != 'all':
                          query += ' AND lower(foodDiet) = ?'
                          params.append(diet.lower())

                       if flavor != 'all':
                           query += ' AND lower(flavor) = ?'
                           params.append(flavor.lower())

                       if region != 'all':
                          query += ' AND lower(region) = ?'
                          params.append(region.lower())

                       if course != 'all':
                           query += ' AND lower(course) = ?'
                           params.append(course.lower())

                       cursor.execute(query, params)
                       food_names = cursor.fetchall()
                       if food_names:
                            print(tabulate(food_names, tablefmt="pretty"))
                       else :
                           print("No food items match the preferences.")
                else:
                   print("No preferences found for the selected user.")
            case '2':
                update = input("1.Add new user\n2.Change goto values\n3.Delete user\nEnter the corresponding number:\n")
                if update == '1':
                    goto_insert_data(conn)
                elif update == '2':
                    cursor.execute('''SELECT * FROM users''')
                    column_names = [description[0] for description in cursor.description]
                    users = cursor.fetchall()
                    print(tabulate(users, headers=column_names, tablefmt="pretty"))
                    # selecting your choice
                    choice = input("Enter the number corresponding to your user choice:\n")
                    user_id = users[int(choice) - 1][0]  # Get the user ID based on choice
                    # getting needed values based on userid
                    flavour , diet,region, course = goto_insert_data(conn)
                    cursor.execute('''UPDATE  goto_food SET foodDiet =?,flavor=?,region=?,course=? WHERE userId = ?''',(user_id,flavour,diet,region,course))
                    # name = input("Enter user name:\n")
                    # cursor.execute('''UPDATE users SET userName=?  WHERE id = ?''',(user_id,name))
                    conn.commit()
                    #goto_insert_data(conn)
                elif update == '3':
                    cursor.execute('''SELECT * FROM users''')
                    column_names = [description[0] for description in cursor.description]
                    users = cursor.fetchall()
                    print(tabulate(users, headers=column_names, tablefmt="pretty"))
                    # selecting your choice
                    choice = input("Enter the number corresponding to your user choice:\n")
                    user_id = users[int(choice) - 1][0]  # Get the user ID based on choice
                    # getting needed values based on userid
                    cursor.execute('''DELETE FROM goto_food WHERE userId = ?''',(user_id,))
                    cursor.execute('''DELETE FROM users WHERE id = ?''',(user_id,))
                    reset_user_ids(conn)
                    conn.commit()
                else:
                    print(sqlite3.Error)
    except sqlite3.Error as e:
        print(e)

def filter_selection(conn):
     
    '''Selecting food as per individuals preference'''
    try:
        cursor = conn.cursor()
        #  importing the preference
        flavour, diet, region, course = food_selection(conn) 

        '''Logic for filtering data'''
        #  no filter 
        if flavour == 'all' and diet == 'all' and region == 'all' and course == 'all':
            cursor.execute('''SELECT * FROM Food_Database''')
        #  filter for Flavor
        elif diet == 'all' and region == 'all' and course == 'all':
            cursor.execute('''SELECT DISTINCT foodName, foodDiet, region, course FROM Food_Database WHERE lower(flavor) = ?''',(flavour,) )
        #  filter for Diet
        elif flavour == 'all' and region == 'all' and course == 'all':
            cursor.execute('''SELECT DISTINCT foodName,flavor,region, course FROM Food_Database WHERE lower(foodDiet) = ?''',(diet,))
        #  filtered for Region
        elif flavour == 'all' and diet == 'all' and course == 'all':
            cursor.execute('''SELECT DISTINCT foodName, flavor, foodDiet, course FROM Food_Database WHERE lower(region) = ?''',(region,))
        #  filter for Course
        elif flavour == 'all' and diet == 'all' and region == 'all' :
            cursor.execute('''SELECT DISTINCT foodName, flavor,foodDiet,region FROM Food_Database WHERE lower(course) = ?''', (course,))
        #  filter for Flavor and Diet
        elif region == 'all' and course == 'all':
            cursor.execute('''SELECT DISTINCT foodName , region, course FROM Food_Database WHERE lower(flavor) = ? AND lower(foodDiet) = ?''',(flavour, diet))
        #  filter for Flavor and Region
        elif  diet == 'all' and course == 'all':
            cursor.execute('''SELECT DISTINCT foodName, foodDiet, course FROM Food_Database WHERE lower(flavor) = ? AND lower(region) = ?''',(flavour,region ))
        #  filter for Flavor and Course
        elif diet == 'all' and region == 'all':
            cursor.execute('''SELECT DISTINCT foodName, foodDiet, region FROM Food_Database WHERE lower(flavor) = ? AND lower(course) = ?''',(flavour, course))
        #  filter for Diet and Region
        elif flavour == 'all' and course == 'all':
            cursor.execute('''SELECT DISTINCT foodName,flavor, course FROM Food_Database WHERE lower(foodDiet) = ? AND lower(region) = ?''',(diet, region))
        #  filter for Diet and Course
        elif flavour == 'all' and region == 'all':
            cursor.execute('''SELECT DISTINCT foodName,flavor, region FROM Food_Database WHERE lower(foodDiet) = ? AND lower(course) = ?''',(diet, course))
        #  filter Region and Course 
        elif flavour == 'all' and diet == 'all':
            cursor.execute('''SELECT DISTINCT foodName, flavor, foodDiet FROM Food_Database WHERE lower(region) = ? AND lower(course) = ?''',(region, course))
        #  filter Flavour, Diet and Region
        elif course == 'all':
            cursor.execute('''SELECT DISTINCT foodName,course FROM Food_Database WHERE lower(flavor) = ? AND lower(foodDiet) = ? AND lower(region) = ?''',(flavour,diet,region))
        #  filter Flavour, Region and Course
        elif diet == 'all':
            cursor.execute('''SELECT DISTINCT foodName, foodDiet FROM Food_Database WHERE lower(flavor) = ? AND lower(region) = ? AND lower(course) = ?''',(flavour,region,course))
        #  filter Flavour, Diet, Course
        elif region == 'all':
            cursor.execute('''SELECT DISTINCT foodName, region FROM Food_Database WHERE lower(flavor) = ? AND lower(foodDiet) = ? AND lower(course) = ?''',(flavour, diet, course))
        #  filter Diet, Region and Course
        elif flavour == 'all':
            cursor.execute('''SELECT DISTINCT foodName, flavor FROM Food_Database WHERE lower(foodDiet) = ? AND lower(region) = ? AND lower(course) = ?''',(diet, region, course))
        #  filter all
        else:
            cursor.execute('''SELECT DISTINCT foodName FROM Food_Database WHERE lower(flavor) = ? AND lower(foodDiet) = ? AND lower(region) = ? AND lower(course) = ?''',(flavour,diet,region,course))
        
        '''Output of filter'''
        column_names = [description[0] for description in cursor.description]
        #print('\t'.join(column_names))
        rows = cursor.fetchall()
        # for row in rows:
        #     print('\t'.join(map(str,row)))
        print(tabulate(rows, headers=column_names, tablefmt="pretty"))
    except sqlite3.Error as e:
        print(e)


