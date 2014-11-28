# coding=utf8
"""
ping.py - Willie Ping Module
Author: Sean B. Palmer, inamidst.com
About: http://willie.dftba.net
"""
from __future__ import unicode_literals

import random
from willie.module import rule, priority, thread, commands


@rule(r'(?i)(hi|hello|hey|hola|buenas|hey)[,]? $nickname[ \t]*$')
def hello(bot, trigger):
    if trigger.owner:
        greeting = random.choice(('No sé quien eres', 'No me has programado bien, error 404', 'Tú no me amas, me cambiaste por Trivial-Bot'))
    else:
        greeting = random.choice(('Hola', 'Hey', 'Buenas'))
    punctuation = random.choice(('', '!'))
    bot.say(greeting + ' ' + trigger.nick + punctuation)


@rule(r'(?i)(Fuck|Screw) you, $nickname[ \t]*$')
def rude(bot, trigger):
    bot.say('Watch your mouth, ' + trigger.nick + ', or I\'ll tell your mother!')


@rule('$nickname!')
@priority('high')
@thread(False)
def interjection(bot, trigger):
    bot.say(trigger.nick + '!')

@commands('ping')
def pong(bot, trigger):
    bot.say(trigger.nick + ': pong?')
