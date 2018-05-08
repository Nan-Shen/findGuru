import tweepy
import time
import os
import sys
import json

FOLLOWING_DIR = './data/following'
MAX_FRIENDS = 200
FRIENDS_OF_FRIENDS_LIMIT = 200

if not os.path.exists(FOLLOWING_DIR):
    os.makedir(FOLLOWING_DIR)

enc = lambda x: x.encode('ascii', errors='ignore')


CONSUMER_KEY = 
CONSUMER_SECRET = '
ACCESS_TOKEN =
ACCESS_TOKEN_SECRET = '

# == OAuth Authentication ==
#
# This mode of authentication is the new preferred way
# of authenticating with Twitter.
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

def get_follower_ids(centre, max_depth=1, current_depth=0, taboo_list=[]):

    print 'current depth: %d, max depth: %d' % (current_depth, max_depth)
    print 'taboo list: ', ','.join([ str(i) for i in taboo_list ])

    if current_depth == max_depth:
        print 'out of depth'
        return taboo_list

    if centre in taboo_list:
        # we've been here before
        print 'Already been here.'
        return taboo_list
    else:
        taboo_list.append(centre)

    try:
        userfname = os.path.join('twitter-users', str(centre) + '.json')
        if not os.path.exists(userfname):
            print 'Retrieving user details for twitter id %s' % str(centre)
            while True:
                try:
                    user = api.get_user(centre)

                    d = {'name': user.name,
                         'screen_name': user.screen_name,
                         'id': user.id,
                         'friends_count': user.friends_count,
                         'followers_count': user.followers_count,
                         'followers_ids': user.followers_ids()}

                    with open(userfname, 'w') as outf:
                        outf.write(json.dumps(d, indent=1))

                    user = d
                    break
                except tweepy.TweepError, error:
                    print type(error)

                    if str(error) == 'Not authorized.':
                        print 'Can''t access user data - not authorized.'
                        return taboo_list

                    if str(error) == 'User has been suspended.':
                        print 'User suspended.'
                        return taboo_list

                    errorObj = error[0][0]

                    print errorObj

                    if errorObj['message'] == 'Rate limit exceeded':
                        print 'Rate limited. Sleeping for 15 minutes.'
                        time.sleep(15 * 60 + 15)
                        continue

                    return taboo_list
        else:
            user = json.loads(file(userfname).read())


        #get friend ids
        screen_name = enc(user['screen_name'])
        fname = os.path.join(FOLLOWING_DIR, screen_name + '.csv')
        friendids = []

        
        if not os.path.exists(fname):
            print 'No cached data for screen name "%s"' % screen_name
            with open(fname, 'w') as outf:
                params = (enc(user['name']), screen_name)
                print 'Retrieving friends for user "%s" (%s)' % params

                # page over friends
                c = tweepy.Cursor(api.friends, id=user['id']).items()

                friend_count = 0
                while True:
                    try:
                        friend = c.next()
                        friendids.append(friend.id)
                        params = (friend.id, enc(friend.screen_name), enc(friend.name))
                        outf.write('%s\t%s\t%s\n' % params)
                        friend_count += 1
                        if friend_count >= MAX_FRIENDS:
                            print 'Reached max no. of friends for "%s".' % friend.screen_name
                            break
                    except tweepy.TweepError:
                        # hit rate limit, sleep for 15 minutes
                        print 'Rate limited. Sleeping for 15 minutes.'
                        time.sleep(15 * 60 + 15)
                        continue
                    except StopIteration:
                        break
        else:
            friendids = [int(line.strip().split('\t')[0]) for line in file(fname)]

        print 'Found %d friends for %s' % (len(friendids), screen_name)

        # get friends of friends
        cd = current_depth
        if cd+1 < max_depth:
            for fid in friendids[:FRIENDS_OF_FRIENDS_LIMIT]:
                taboo_list = get_follower_ids(fid, max_depth=max_depth,
                                     current_depth=cd+1, taboo_list=taboo_list)

        if cd+1 < max_depth and len(friendids) > FRIENDS_OF_FRIENDS_LIMIT:
            print 'Not all friends retrieved for %s.' % screen_name

    except Exception, error:
       print 'Error retrieving followers for user id: ', centre
       print error

       if os.path.exists(fname):
            os.remove(fname)
            print 'Removed file "%s".' % fname

       sys.exit(1)

    return taboo_list

