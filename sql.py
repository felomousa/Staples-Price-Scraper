import sqlite3

conn = sqlite3.connect('StaplesDB')
c = conn.cursor()

c.execute('''CREATE TABLE staples(productID TEXT, productName TEXT, price INT, discount INT)''')

# c.execute('''INSERT INTO Staples VALUES(?,?,?)''', (ProductID, ProductName, Price))
# conn.commit()

# c.execute('''SELECT ProductName FROM Staples''')
# results = c.fetchall()

# print(results)