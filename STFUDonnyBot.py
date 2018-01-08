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

import json, pprint, random

from tweepy.streaming import StreamListener                     # http://www.tweepy.org
from tweepy import OAuthHandler
from tweepy import Stream
from http.client import IncompleteRead

import pid                                                      # https://pypi.python.org/pypi/pid/

import patrick_logger                                           # https://github.com/patrick-brian-mooney/python-personal-library/
import social_media as sm                                       # https://github.com/patrick-brian-mooney/python-personal-library/
from social_media_auth import Trump_client, Trump_client_for_personal_account   # Unshared module that contains my authentication constants     # FIXME

consumer_key, consumer_secret = Trump_client['consumer_key'], Trump_client['consumer_secret']
access_token, access_token_secret = Trump_client['access_token'], Trump_client['access_token_secret']

target_accounts = ['realDonaldTrump']
image_URLs = ['https://media.giphy.com/media/cdxGGMh7UDuAE/giphy.gif',                                                  # while bowling
              'http://s2.quickmeme.com/img/1f/1fd3eb2d600dfff5506ff549f5fd58fc7949f4f56eea21a8ddd689b2a13eb1a5.jpg',    # out of your element
              'https://media1.tenor.com/images/98e1c9a96042b4ea6fae90b43ebc9fa5/tenor.gif?itemid=5761606',              # at the theater
              ]

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


class TrumpListener(StreamListener):
    """Of all the people on Twitter, Donald Trump is probably the least worth listening to. So let's
    create a bot to handle the drudgery for us.
    """
    def on_data(self, data):
        try:
            data = json.loads(data)
            try:
                if data['user']['id_str'] in target_accounts:       # If it's the account we're watching, reply to it. 
                    pass                                            # FIXME: actually reply
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
        with pid.PidFile(piddir=home_dir):
            l = TrumpListener()
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
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
                    break
    except pid.PidFileError:
        log_it("Already running! Quitting ...", 0)
        sys.exit()
