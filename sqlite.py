import sqlite3

## code to connect to sqlite database
connection = sqlite3.connect('student.db')


# create a cursor obj to insert records create  tables 
cursor = connection.cursor()

# create the table 
table_info = """
CREATE TABLE IF NOT EXISTS STUDENT (
    NAME VARCHAR(25),
    CLASS VARCHAR(25),
    SECTION VARCHAR(25),
    MARKS INT
); 
"""
cursor.execute(table_info) 

## insert some more  records

cursor.execute('''Insert into STUDENT values('Rahul','Data Science','A',60)''')
cursor.execute('''Insert into STUDENT values('Raj','Data Science','B',91)''')
cursor.execute('''Insert into STUDENT values('Ravi','DevOps','C',80)''')
cursor.execute('''Insert into STUDENT values('Aryan','Data Science','A',100)''')
cursor.execute('''Insert into STUDENT values('boy','DevOps','B',95)''')

## display all records 

print("The inserted ercords are")
data = cursor.execute('''Select * from STUDENT''')
for row in data:
    print(row)

## commit the changes in database
connection.commit()
connection.close()
