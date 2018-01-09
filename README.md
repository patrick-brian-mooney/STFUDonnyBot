# STFUDonnyBot
8 Jan 2017

## Overview and Rationale

Twitter recently [said](https://blog.twitter.com/official/en_us/topics/company/2017/world-leaders-and-twitter.html) that normal rules about civility and bullying don't apply to Donald Trump. It seems to me like it's time for a test to see how far that dispensation extends: is it a special privilege for Trump (and perhaps other world leaders)? Or have the normal rules of discourse about *speaking back* to world leaders also been suspended?

All Twitter really says is that world leaders on Twitter have special status because of "their outsized impact on our society" and that their reason for allowing world leaders to continue to behave badly on Twitter is because doing anything else "would certainly hamper necessary discussion around their words and actions." That is to say: this behavior is only acceptable because that's a necessary precondition of people engaging in a conversation about it. This bot attempts to help contribute to that very conversation by repeatedly saying something that definitely needs to be said over and over.

Twitter also says that they "are working to make Twitter the best place to see and freely discuss everything that matters." Because that's what Twitter is about, right? Discussing everything that matters? In the spirit of that statement, this bot says something that, in the context in which the bot operates, very much matters and that needs to be said much more often in our society.

## Operation

This bot, which is <a rel="me author" href="https://twitter.com/STFUDonnyBot">@STFUDonnyBot</a> on Twitter, watches the <a rel="nofollow" href="https://twitter.com/realDonaldTrump">@realDonaldTrump</a> account on Twitter. When that account tweets, this bot tweets a reply consisting of a GIF of Walter Sobcheck from *The Big Lebowski* saying "Shut the fuck up, Donny."

It is written in Python 3 and requires the [Tweepy](http://www.tweepy.org/) and [pid](https://pypi.python.org/pypi/pid/) modules, plus a few modules from [my own personal library](https://github.com/patrick-brian-mooney/python-personal-library/). See the code for details.