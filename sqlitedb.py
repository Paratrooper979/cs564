import web

db = web.database(dbn='sqlite',
                  db='AuctionBase'
                  )


######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')


# initiates a transaction on the database
def transaction():
    return db.transaction()


# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except Exception as e:
#     t.rollback()
#     print str(e)
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

# returns the current time from your database
def getTime():
    # the correct column and table name in your database
    query_string = 'select Time from CurrentTime'
    results = query(query_string)
    # alternatively: return results[0]['currenttime']
    return results[0].Time  # TODO: update this as well to match the
    # column name


# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!
def getItemById(item_id):
    query_string = 'select * from Items where ItemID = $itemID'
    result = query(query_string, {'itemID': item_id})
    try:
        return result[0]
    except IndexError:
        return None


# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars={}):
    return list(db.query(query_string, vars))


#####################END HELPER METHODS#####################

# TODO: additional methods to interact with your database,
# e.g. to update the current time

def setTime(currentTime):
    t = transaction()
    try:
        db.update('CurrentTime', where='Time', Time=currentTime)
    except Exception as e:
        t.rollback()
        print str(e)
    else:
        t.commit()


def addBid(user_id, item_id, amount, time):
    t = transaction()
    try:
        db.insert('Bids', UserID=user_id, ItemID=item_id, Amount=amount, Time=time)
    except Exception as e:
        t.rollback()
        print str(e)
    else:
        t.commit()


def updateItem(item_id, end_time, buy_price):
    t = transaction()
    try:
        db.update('Items', where='ItemID=$item_id', item_id=item_id, Ends=end_time, Buy_Price=buy_price)
    except Exception as e:
        t.rollback()
        print str(e)
    else:
        t.commit()


def getUserById(user_id):
    query_string = 'select * from Users where UserID = $userID'
    result = query(query_string, {'userID': user_id})
    try:
        return result[0]
    except IndexError:
        return None


def getCategoryById(item_id):
    query_string = 'select Category from Categories where ItemID = $itemID'
    result = query(query_string, {'itemID': item_id})
    try:
        return result
    except IndexError:
        return None


def getBidsById(item_id):
    query_string = 'select * from Bids where ItemID = $itemID'
    result = query(query_string, {'itemID': item_id})
    try:
        return result
    except IndexError:
        return None


def getWinnerOfAuction(item_id):
    query_string = 'select Users.* from Users, Bids where ItemID=$itemID and ' \
                   'Amount = (select max(Amount) from Bids where ItemID=$itemID)'
    result = query(query_string, {'itemID': item_id})
    try:
        return result
    except IndexError:
        return None


# TODO
def getItem(item_id, user_id, category, item_desc, min_price, max_price, status):
    # dict = {}
    # if item_id != '':
    #     dict['item_id'] = item_id
    # if user_id != '':
    #     dict['user_id'] = user_id
    # if category != '':
    #     dict['category'] = category
    # if item_desc != '':
    #     dict['item_desc'] = item_desc
    # if min_price != '':
    #     dict['min_price'] = min_price
    # if max_price != '':
    #     dict['max_price'] = max_price
    # if status != 'All':
    #     dict['status'] = status
    #
    # query_string = 'select * from Items'
    # # if the user does not entry any search criteria, then just simply return all items from that table
    # if not dict:
    #     return query(query_string)
    #
    # # So the user typed something
    # query_string += ' where'
    #
    # if 'item_id' in dict:
    #     query_string += ' ItemID = $itemID'
    #     query_string += ' and'
    # if 'user_id' in dict:
    #     query_string += ' Seller_UserID = $userID'
    #     query_string += ' and'
    # if 'category' in dict:
    #     query_string += ' '

    pass
