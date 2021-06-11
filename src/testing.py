from database import UsersSQL

test=UsersSQL()

print(test.get_preferences())

"""
#generate column names to be placed in a query SQL
with open('quryfile.txt',mode='w') as file:
    for i in range(1,1001):
        file.write(f'coin_{i} VARCHAR(300), \n pct_{i} FLOAT,\n')
"""