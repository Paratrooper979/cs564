#!/usr/bin/env python

import sys;

sys.path.insert(0, 'lib')  # this line is necessary for the rest
import os  # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime


###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
                            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
                            extensions=extensions,
                            )
    jinja_env.globals.update(globals)

    web.header('Content-Type', 'text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)


#####################END HELPER METHODS#####################

urls = ('/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/add_bid', 'add_bid',
        '/search', 'search',
        '/search_auction', 'search_auction',
    # TODO: add additional URLs here
    # first parameter => URL, second parameter => class name
        )


class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()
        return render_template('curr_time.html', time=current_time)


class select_time:
    # Aanother GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html')

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss'];
        enter_name = post_params['entername']

        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)

        sqlitedb.setTime(select_time)

        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('select_time.html', message=update_message)


class add_bid:

    def GET(self):
        return render_template('add_bid.html')

    def POST(self):

        post_params = web.input()
        user_id = post_params['userID']
        item_id = post_params['itemID']
        amount = post_params['price']
        time = sqlitedb.getTime()

        if user_id == '' or item_id == '' or amount == '':
            return render_template('add_bid.html', message='These fields cannot be empty')

        item = sqlitedb.getItemById(item_id)
        if item is None:
            return render_template('add_bid.html', message='ItemID not match')

        user = sqlitedb.getUserById(user_id)
        if user is None:
            return render_template('add_bid.html', message='UserID not match')

        if amount < 0:
            return render_template('add_bid.html', message='Price cannot be negative')

        if amount <= item.First_Bid:
            return render_template('add_bid.html', message='Price is lower than minimum price seller set')

        if string_to_time(time) >= string_to_time(item.Ends) or string_to_time(time) < string_to_time(item.Started):
            return render_template('add_bid.html',
                                   message='No auction may have a bid before its start time or after its end time.')

        if user_id == item.Seller_UserID:
            return render_template('add_bid.html', message='A user may not bid on an item he or she is also selling')

        # TODO: No auction may have two bids at the exact same time. Don't know how to do that

        # not sure if triggers already handled these constraint, if not, we may need to handle in this funciton

        item.Number_of_Bids += 1
        item.Currently = amount

        # Close the auction if amount is greater than buy_price the seller set
        if amount >= item.Buy_Price and item.Buy_Price is not None:
            sqlitedb.updateItem(item_id, time, amount)
            msg = '(Congratulations. Your bid %s achieves the buy_price and this %s is now yours)' % \
                  (amount, item.Name)
        else:
            msg = '(You just added a bid on item %s)' % item.Name

        sqlitedb.addBid(user_id, item_id, amount, time)
        return render_template('add_bid.html', message=msg)

class search:

    def GET(self):
        return render_template('search.html')

    def POST(self):
        # TODO
        post_params = web.input()
        item_id = post_params['itemID']
        user_id = post_params['userID']
        category = post_params['category']
        item_desc = post_params['description']
        min_price = post_params['minPrice']
        max_price = post_params['maxPrice']
        status = post_params['status']

        item_array = [item_id, user_id, category, item_desc, min_price, max_price, status]

        pass


class search_auction:

    def GET(self, item_id):
        item_info = sqlitedb.getItemById(item_id)
        category = sqlitedb.getCategoryById(item_id)
        bids = sqlitedb.getBidsById(item_id)

        if item_info is None or category is None or bids is None:
            msg = 'Item_id not match'
            return render_template('search_auction.html', message=msg)

        if string_to_time(curr_time) > string_to_time(item_info.Ends):
            status = 'closed'
            winner = sqlitedb.getWinnerOfAuction(item_id)
        elif string_to_time(curr_time) > string_to_time(item_info.Started):
            status = 'open'
            winner = None
        else:
            status = 'Not Started'
            winner = None

        return render_template('search_auction.html', item=item_info, category=category,
                               status=status, bids=bids, winner=winner)


###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
