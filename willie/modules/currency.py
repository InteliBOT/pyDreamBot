# coding=utf8
"""currency.py - Willie Exchange Rate Module
Copyright 2013 Edward Powell, embolalia.com
Licensed under the Eiffel Forum License 2

http://willie.dftba.net
"""
from __future__ import unicode_literals

import json
from lxml import etree
import re

from willie import web
from willie.module import commands, example, NOLIMIT
import json

# The Canadian central bank has better exchange rate data than the Fed, the
# Bank of England, or the European Central Bank. Who knew?
base_url = 'http://www.bankofcanada.ca/stats/assets/rates_rss/noon/en_{}.xml'
regex = re.compile(r'''
    (\d+(?:\.\d+)?)        # Decimal number
    \s*([a-zA-Z]{3})       # 3-letter currency code
    \s+(?:in|as|of|to|en|a|de)\s+  # preposition
    ([a-zA-Z]{3})          # 3-letter currency code
    ''', re.VERBOSE)


def get_rate(code):
    if code == 'CAD':
        return 1, 'Dolar canadience'
    elif code == 'BTC':
        rates = json.loads(web.get('https://api.bitcoinaverage.com/ticker/all'))
        return 1 / rates['CAD']['24h_avg'], 'Bitcoin 24h'

    data, headers = web.get(base_url.format(code), dont_decode=True, return_headers=True)
    if headers['_http_status'] == 404:
        return False, False
    xml = etree.fromstring(data)
    namestring = xml.find('{http://purl.org/rss/1.0/}channel/'
                          '{http://purl.org/rss/1.0/}title').text
    #name = namestring[len('Bank of Canada noon rate: '):]
    #name = re.sub(r'\s*\(noon\)\s*', '', name)
    metajson = json.loads(open("willie/modules/json/iso4217.json").read())
    name = metajson[code]
    rate = xml.find(
        '{http://purl.org/rss/1.0/}item/'
        '{http://www.cbwiki.net/wiki/index.php/Specification_1.1}statistics/'
        '{http://www.cbwiki.net/wiki/index.php/Specification_1.1}exchangeRate/'
        '{http://www.cbwiki.net/wiki/index.php/Specification_1.1}value').text
    return float(rate), name


@commands('cur', 'currency', 'exchange', 'cambio', 'moneda')
@example('%cur 20 EUR en USD')
def exchange(bot, trigger):
    """Muestra la taza de cambio de monedas del mundo"""
    if not trigger.group(2):
        return bot.reply("No hay nada para buscar, ejemplo: %cur 20 EUR in USD")    
    match = regex.match(trigger.group(2))
    if not match:
        # It's apologetic, because it's using Canadian data.
        bot.reply("Lo siento, no entiendo esa entrada.")
        return NOLIMIT

    amount, of, to = match.groups()
    try:
        amount = float(amount)
    except:
        bot.reply("Lo siento, no entiendo esa entrada.")
    display(bot, amount, of, to)

def display(bot, amount, of, to):
    of = of.upper()
    to = to.upper()
    if not amount:
        bot.reply("Cero es cero!")
    try:
        of_rate, of_name = get_rate(of)
        if not of_name:
            bot.reply("Moneda desconocida: %s" % of)
            return
        to_rate, to_name = get_rate(to)
        if not to_name:
            bot.reply("Moneda desconocida: %s" % to)
            return
    except Exception as e:
        raise
        bot.reply("Algo ha pasado, y no pude obtener información actualizada")
        return NOLIMIT

    result = amount / of_rate * to_rate
    bot.say("{} {} ({}) = {} {} ({})".format(amount, of, of_name,
                                           result, to, to_name))


@commands('btc', 'bitcoin')
@example('%btc 20 EUR')
def bitcoin(bot, trigger):
    #if 2 args, 1st is number and 2nd is currency. If 1 arg, it's either the number or the currency.
    to = trigger.group(4)
    amount = trigger.group(3)
    if not to:
        to = trigger.group(3) or 'USD'
        amount = 1

    try:
        amount = float(amount)
    except:
        bot.reply("Lo siento, no entiendo esa entrada")
        return NOLIMIT

    display(bot, amount, 'BTC', to)
