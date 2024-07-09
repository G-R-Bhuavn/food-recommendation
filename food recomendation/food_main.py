from food_function import food_file,create_connection,create_food_info_table,delete,delete_duplicates,insert_food_data,print_Table,filter_selection,goto_preferences_functions

database = 'foodData.db'
conn = create_connection(database)

if conn is not None:
    create_food_info_table(conn)
    insert_food_data(conn,food_file)
    #delete_duplicates(conn)
    #delete(conn)
    #print_Table(conn)
    continue_loop = True
    # while continue_loop:
    choice = input("Enter your choice:\n1.Go-to\n2.Choose your order\n3.Exit\nEnter the number of your choice\n")
    match(choice):
           case '1':
            goto_preferences_functions(conn)
           case '2':
            filter_selection(conn)

        #    case '3':
        #     continue_loop = False

    
else:
    print("Error! Cannot create the database connection.")