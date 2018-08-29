import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('~/Code/InstaPy')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

import sys
from distutils.util import strtobool

import time
from tempfile import gettempdir

from selenium.common.exceptions import NoSuchElementException

from instapy import InstaPy

import mysql.connector

if len(sys.argv) != 2:
    print("Not enough parameters")
    exit()

brand_id = sys.argv[1]

cnx = mysql.connector.connect(user=os.getenv("DB_USERNAME"), 
                              password=os.getenv("DB_PASSWORD"),
                              host=os.getenv("DB_HOST"),
                              database=os.getenv("DB_NAME"))

cursor = cnx.cursor()

query = """SELECT id,username,password,potency_ratio,max_followers,max_following,min_followers,min_following,
            set_do_comment,set_do_comment_percentage,set_do_follow,set_do_follow_percentage,set_do_follow_times,set_user_interact,
            interact_randomize,interact_percentage
          FROM configurations WHERE id = %(brand_id)s"""

cursor.execute(query, { 'brand_id': brand_id })

for (id,username,password,potency_ratio,max_followers,max_following,min_followers,min_following,
            set_do_comment,set_do_comment_percentage,set_do_follow,set_do_follow_percentage,set_do_follow_times,set_user_interact,
            interact_randomize,interact_percentage) in cursor:
    insta_username = username
    insta_password = password
    potency_ratio = float(potency_ratio)
    max_followers = int(max_followers)
    max_following = int(max_following)
    min_followers = int(min_followers)
    min_following = int(min_following)
    set_do_comment = set_do_comment 
    set_do_comment_percentage = set_do_comment_percentage 
    set_do_follow = set_do_follow 
    set_do_follow_percentage = set_do_follow_percentage 
    set_do_follow_times = set_do_follow_times 
    set_user_interact = set_user_interact 
    interact_randomize = interact_randomize 
    interact_percentage = interact_percentage 

cursor.close()
cnx.close()

# set headless_browser=True if you want to run InstaPy on a server

# set these in instapy/settings.py if you're locating the
# library in the /usr/lib/pythonX.X/ directory:
#   Settings.database_location = '/path/to/instapy.db'
#   Settings.chromedriver_location = '/path/to/chromedriver'

session = InstaPy(username=insta_username,
                  password=insta_password,
                  headless_browser=strtobool(os.getenv("HEADLESS_BROWSER")),
                #   headless_browser=False,
                  multi_logs=strtobool(os.getenv("MULTI_LOGS")))

try:
    session.login()

    # settings
    session.set_relationship_bounds(enabled=True,
				 potency_ratio=-potency_ratio,
				  delimit_by_numbers=True,
				   max_followers=max_followers,
				    max_following=max_following,
				     min_followers=max_following,
				      min_following=min_following)
    session.set_do_comment(set_do_follow, percentage=set_do_follow_percentage)
    session.set_comments([  
                        '@{} Nice!',
                        '@{} Great post!',
                        '@{} Excellent post!',
                        '@{} Stunning!',
                        '@{} Great job!'
    ])
    session.set_dont_include(['f4f','follow4follow','friend1', 'friend2', 'friend3'])
    session.set_dont_like(['pizza', 'nsfw'])

    # actions
    session.set_do_follow(enabled=set_do_follow, percentage=set_do_follow_percentage, times=set_do_follow_percentage)
    session.like_by_tags(['miamikeratin','keratin','keratintreatment','botoxforhair','hairstyle','miamihairstylist','miamihairsalon','miamihairstyles'], amount=50, interact=True)

except Exception as exc:
    # if changes to IG layout, upload the file to help us locate the change
    if isinstance(exc, NoSuchElementException):
        file_path = os.path.join(gettempdir(), '{}.html'.format(time.strftime('%Y%m%d-%H%M%S')))
        with open(file_path, 'wb') as fp:
            fp.write(session.browser.page_source.encode('utf8'))
        print('{0}\nIf raising an issue, please also upload the file located at:\n{1}\n{0}'.format(
            '*' * 70, file_path))
    # full stacktrace when raising Github issue
    raise

finally:
    # end the bot session
    session.end()
