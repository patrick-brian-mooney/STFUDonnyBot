#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Twitter recently announced that their normal rules about bullying and civility
don't apply to the accounts of world leaders, this bot tests whether those
rules are also interpreted differently for people speaking back to bullying
world leaders. In order to test this, it says something that, though perhaps
not civil, is certainly something that needs to be said much more often.

That is, STFUDonnyBot is a bot that waits for @realDonaldTrump to tweet, then
replies with an image GIF of Walter Sobchek saying 'Shut the fuck up, Donny.'

STFUDonnyBot is copyright 2018 by Patrick Mooney. It is released under the GNU
GPL, either version 3 or (at your option) any later version. See the LICENSE
file for details.
"""

import glob, json, pprint, random, requests, sys, time

import tweepy
from tweepy.streaming import StreamListener                     # http://www.tweepy.org
from tweepy import OAuthHandler
from tweepy import Stream
from http.client import IncompleteRead

import pid                                                      # https://pypi.python.org/pypi/pid/

from patrick_logger import log_it                               # https://github.com/patrick-brian-mooney/python-personal-library/
from social_media_auth import STFUDonnyBot_client               # Unshared module that contains my authentication constants

consumer_key, consumer_secret = STFUDonnyBot_client['consumer_key'], STFUDonnyBot_client['consumer_secret']
access_token, access_token_secret = STFUDonnyBot_client['access_token'], STFUDonnyBot_client['access_token_secret']

# target_accounts = ['realDonaldTrump']
target_accounts = {'98912248': 'patrick_mooney'}
image_directory = 'STFU/'
API = None      # This will be redefined as the Tweepy API object during startup.

# OK, let's work around a problem that comes from the confluence of Debian's ancient packaging and rapid changes in Python's Requests package.
try:
    x = ProtocolError               # Test for existence.
    log_it('NOTE: We are running on a system where ProtocolError is properly defined', 2)
except Exception as e:              # If it's not defined, try to import it.
    try:
        log_it('WARNING: no ProtocolError (got exception "%s"); trying requests.packages.urllib3.exceptions instead' % e)
        from requests.packages.urllib3.exceptions import ProtocolError
        log_it('NOTE: successfully imported from requests')
    except Exception as e:
        try:
            log_it('WARNING: still got exception "%s"; trying from xmlrpclib instead' % e)
            from xmlrpclib import ProtocolError
            log_it('NOTE: successfully imported from xmlprclib')
        except Exception as e:      # If we can't import it, define it so the main loop's Except clause doesn't crash on every exception.
            log_it('WARNING: still got exception "%s"; defining by fiat instead' % e)
            ProtocolError = IncompleteRead

def reply(original_tweet_data):
    """#FIXME """
    tweetID = original_tweet_data['id']
    which_user = original_tweet_data['user']['screen_name']
    which_image = random.choice(glob.glob(image_directory + "*"))
    tweet_URL = 'https://twitter.com/%s/status/%s' % (which_user, tweetID)
    ret = API.update_with_media(filename=which_image, status="@%s" % (which_user), in_reply_to_status_id=tweetID)
    # Next, archive it in the Internet Archive
    req = requests.get(tweet_URL)
    for i in req.iter_content(chunk_size=100000): pass
    # Now, add the archived URL to our own local archive.
    with open('archives', mode='a') as archive_file:
        archive_file.write('http://web.archive.org/web/*/' + tweet_URL + '\n')
    return ret

class TrumpListener(StreamListener):
    """Of all the people on Twitter, Donald Trump is probably the least worth listening to. So let's
    create a bot to handle the drudgery for us.
    """
    def on_data(self, data):
        try:
            data = json.loads(data)
            try:
                if data['user']['id_str'] in target_accounts:       # If it's the account we're watching, reply to it.
                    reply(data)
            except KeyError:
                log_it('INFO: we got minimal data again', 1)
                log_it('... value of data is:\n\n%s\n\n' % pprint.pformat(data), 1)
        except BaseException as e:
            log_it('ERROR: \n  Exception is:' + pprint.pformat(e), -1)
            log_it('  Value of data is:', -1)
            log_it(pprint.pformat(data), -1)
            raise
        return True

    def on_error(self, status):
        log_it("ERROR: %s" % status, -1)

if __name__ == '__main__':
    try:
        with pid.PidFile(piddir='/home/patrick/Documents/programming/python_projects/STFUDonnyBot'):
            l = TrumpListener()
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            API = tweepy.API(auth)
            log_it("... OK, we're set up, and about to watch %s" % ', '.join(target_accounts), 0)
            while True:
                try:
                    stream = Stream(auth, l)
                    stream.filter(follow=target_accounts, stall_warnings=True)
                except (IncompleteRead, ProtocolError, requests.packages.urllib3.exceptions.ReadTimeoutError) as e:
                    # Sleep some before trying again.
                    log_it("WARNING: received error %s; sleeping and trying again ..." % e)
                    time.sleep(15)
                    continue
                except KeyboardInterrupt:
                    stream.disconnect()
                    raise
    except pid.PidFileError:
        log_it("Already running! Quitting ...", 0)
        sys.exit()
