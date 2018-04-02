#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Twitter recently announced that their normal rules about bullying and civility
don't apply to the accounts of world leaders. This bot tests whether those
rules are also interpreted differently for people speaking back to bullying
world leaders. In order to test this, it says something that, though perhaps
not civil, is certainly something that needs to be said much more often.

That is, STFUDonnyBot is a bot that waits for @realDonaldTrump to tweet, then
replies with an image GIF of John Goodman as Walter Sobchak in The Big Lebowski
saying "Shut the fuck up, Donny."

STFUDonnyBot is copyright 2018 by Patrick Mooney. It is released under the GNU
GPL, either version 3 or (at your option) any later version. See the LICENSE
file for details.
"""

import glob, json, os, pprint, random, requests, sys, time

import tweepy
from tweepy.streaming import StreamListener                     # http://www.tweepy.org
from tweepy import OAuthHandler
from tweepy import Stream
from http.client import IncompleteRead

import pid                                                      # https://pypi.python.org/pypi/pid/

from social_media_auth import STFUDonnyBot_client               # Unshared module that contains my authentication constants
import patrick_logger                                           # https://github.com/patrick-brian-mooney/python-personal-library/
from patrick_logger import log_it

patrick_logger.verbosity_level = 2

consumer_key, consumer_secret = STFUDonnyBot_client['consumer_key'], STFUDonnyBot_client['consumer_secret']
access_token, access_token_secret = STFUDonnyBot_client['access_token'], STFUDonnyBot_client['access_token_secret']

# target_accounts = {'25073877': 'realDonaldTrump'}
target_accounts = {'98912248': 'patrick_mooney'}
API = None      # This will be redefined as the Tweepy API object during startup.

base_dir = '/STFUDonnyBot'
image_directory = os.path.join(base_dir, 'STFU/')
URL_archive_file = os.path.join(base_dir, 'archives')

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
        except Exception as e:      # If we can't import it, define it by fiat, so the main loop's Except clause doesn't crash on every exception.
            log_it('WARNING: still got exception "%s"; defining by fiat instead' % e)
            ProtocolError = IncompleteRead

def IArchive_it(url):
    """Saves the document at URL to the Internet Archive's ... well, archive."""
    req = requests.get('http://web.archive.org/web/*/' + url)
    for i in req.iter_content(chunk_size=100000): pass

def reply(tweetID, which_user):
    """Given a tweet to which the bot should reply, this function does four things:
        1. Replies to that tweet.
        2. Archives the reply using the Internet Archive.
        3. Adds the IArchive URL to a list of archived replies that this script
           has made.
        4. Uses the IArchive to archive a copy of the bot's profile page on Twitter.

    TWEETID is the ID# of the tweet to which we're replying. WHICH_USER is the
    username of the user who sent the tweet.
    """
    log_it("OK, we're responding to tweet ID# %s from user %s" % (tweetID, which_user), 1)    
    which_image = random.choice(glob.glob(image_directory + "*"))
    tweet_URL = 'https://twitter.com/%s/status/%s' % (which_user, tweetID)
    ret = API.update_with_media(filename=which_image, status="@%s" % (which_user), in_reply_to_status_id=tweetID)

    log_it("Responded with image '%s'; archiving at the Internet Archive ... " % os.path.basename(which_image), 2)
    IArchive_it(tweet_URL)
    IArchive_it('http://twitter.com/STFUDonnyBot/with_replies')
    
    log_it("Saving archived URL to local list", 3)
    with open(URL_archive_file, mode='a') as archive_file:
        archive_file.write('http://web.archive.org/web/*/' + tweet_URL + '\n')
    return ret

class TrumpListener(StreamListener):
    """Of all the people on Twitter, Donald Trump is probably the least worth listening to. So let's
    create a bot to handle the drudgery of listening to him for us.
    """
    def on_data(self, data):
        try:
            log_it("Twitter gave us the following data:\n\n" + data, 4)            
            decoded_data = json.loads(data)
            try:
                if decoded_data['user']['id_str'] in target_accounts:       # If it's (one of) the account(s) we're watching, reply to it.
                    reply(decoded_data['id'], decoded_data['user']['screen_name'])
                else:
                    log_it("WARNING: Twitter is giving us irrelevant data again:\n\n" + data, 2)
            except KeyError:
                log_it('INFO: we got minimal data again', 1)
                log_it('... value of data is:\n\n%s\n\n' % data, 1)
        except BaseException as e:
            log_it('ERROR: \n  Exception is:' + pprint.pformat(e), -1)
            log_it('  Value of data is:', -1)
            log_it(data, -1)
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
