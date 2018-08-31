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
            interact_randomize,interact_percentage,like_amount
          FROM configurations WHERE id = %(brand_id)s"""

cursor.execute(query, { 'brand_id': brand_id })

for (id,username,password,potency_ratio,max_followers,max_following,min_followers,min_following,
            set_do_comment,set_do_comment_percentage,set_do_follow,set_do_follow_percentage,set_do_follow_times,set_user_interact,
            interact_randomize,interact_percentage,like_amount) in cursor:
    insta_username              = username
    insta_password              = password
    potency_ratio               = float(potency_ratio)
    max_followers               = int(max_followers)
    max_following               = int(max_following)
    min_followers               = int(min_followers)
    min_following               = int(min_following)
    set_do_comment              = bool(set_do_comment)
    set_do_comment_percentage   = int(set_do_comment_percentage) 
    set_do_follow               = bool(set_do_follow)
    set_do_follow_percentage    = int(set_do_follow_percentage)
    set_do_follow_times         = int(set_do_follow_times)
    set_user_interact           = bool(set_user_interact)
    interact_randomize          = bool(interact_randomize)
    interact_percentage         = int(interact_percentage)
    like_amount                 = int(like_amount)

cursor.close()

# Results with brand's comments
comment_cursor = cnx.cursor()

query = """SELECT comment
          FROM comments WHERE brand_id = %(brand_id)s ORDER BY RAND()"""

comment_cursor.execute(query, { 'brand_id': brand_id })

results = comment_cursor.fetchall()

for i in zip(*results):
    comments = list(i)

comment_cursor.close()

# Results with brand's tags
tag_cursor = cnx.cursor()

query = """SELECT tag
          FROM tags WHERE brand_id = %(brand_id)s ORDER BY RAND()"""

tag_cursor.execute(query, { 'brand_id': brand_id })

results = tag_cursor.fetchall()

for i in zip(*results):
    tags = list(i)

tag_cursor.close()

cnx.close()

dont_includes = ['f4f','follow4follow','friend1', 'friend2', 'friend3']
dont_likes = ['nsfw']

session = InstaPy(username=insta_username,
                  password=insta_password,
                  headless_browser=strtobool(os.getenv("HEADLESS_BROWSER")),
                #   headless_browser=False,
                  multi_logs=strtobool(os.getenv("MULTI_LOGS")))

try:
    session.login()

    # settings
    session.set_relationship_bounds(
        enabled=True,
		potency_ratio=potency_ratio,
		delimit_by_numbers=True,
		max_followers=max_followers,
		max_following=max_following,
		min_followers=min_following,
		min_following=min_following
    )

    # comments
    session.set_do_comment(set_do_follow, percentage=set_do_follow_percentage)
    session.set_comments(comments)

    # donts
    session.set_dont_include(dont_includes)
    session.set_dont_like(dont_likes)

    # actions
    session.set_do_follow(enabled=set_do_follow, percentage=set_do_follow_percentage, times=set_do_follow_percentage)
    session.set_user_interact(randomize=interact_randomize, percentage=interact_percentage)
    session.like_by_tags(tags, amount=like_amount)

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
