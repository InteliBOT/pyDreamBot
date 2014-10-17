# coding=utf8
"""
translate.py - Willie Translation Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright © 2013-2014, Elad Alfassa <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""
from __future__ import unicode_literals
from willie import web
from willie.module import rule, commands, priority, example
from microsofttranslator import Translator
import json
import sys
import random
import os
mangle_lines = {}
if sys.version_info.major >= 3:
    unicode = str


def configure(config):
    """

    | [translate] | example | purpose |
    | ---- | ------- | ------- |
    | research | True | Enable research mode (logging) for .mangle |
    | collect_mangle_lines | False | Collect mangle lines to allow .mangle the last message in the channel |
    """
    if config.option('Enable bing', False):
        config.add_section('translate')
        config.interactive_add('translate', 'bing_user', 'Bing Api user', 'bing')
        config.interactive_add('translate', 'bing_pass', 'Bing Api password', 'cakeisalie')
def translate_bing(text, in_lang, out_lang, bot):
    if not bot.config.has_option('translate', 'bing_user') or not bot.config.has_option('translate', 'bing_pass'):
        return 'No se ha habilitado el uso de bing en este bot!'
    else:
        user = bot.config.translate.bing_user
        password = bot.config.translate.bing_pass
    translator = Translator(user, password)
    if in_lang == 'auto':
       return translator.translate(text, out_lang)
    else:
       return translator.translate(text, out_lang, in_lang)

def translate(text, in_lang='auto', out_lang='en'):
    raw = False
    if unicode(out_lang).endswith('-raw'):
        out_lang = out_lang[:-4]
        raw = True

    headers = {
        'User-Agent': 'Mozilla/5.0' +
        '(X11; U; Linux i686)' +
        'Gecko/20071127 Firefox/2.0.0.11'
    }

    url_query = {
        "client": "t",
        "sl": in_lang,
        "tl": out_lang,
        "q": text,
    }
    query_string = "&".join(
        "{key}={value}".format(key=key, value=value)
        for key, value in url_query.items()
    )
    url = "http://translate.google.com/translate_a/t?{query}".format(query=query_string)
    result = web.get(url, timeout=40, headers=headers)

    while ',,' in result:
        result = result.replace(',,', ',null,')
        result = result.replace('[,', '[null,')

    data = json.loads(result)

    if raw:
        return str(data), 'en-raw'

    try:
        language = data[2]  # -2][0][0]
    except:
        language = '?'

    return ''.join(x[0] for x in data[0]), language

@commands('translate', 'tr', 'traducir')
@example('%tr :en :fr my dog', '"mon chien" (en-fr)')
@example('%tr היי', '"Hi" (iw-en)')
@example('%tr mon chien', '"my dog" (fr-en)')
def tr2(bot, trigger):
    """Traduce un texto instantaneamente usando el traductor de Google"""
    if not trigger.group(2):
        return bot.reply('Para usar el traductor ingresa "%tr [idioma origen] [idioma destino] [texto a traducir]"')
    command = trigger.group(2)

    args = command.split(' ')
    phrase = ' '.join(args[2:])

    if (len(phrase) > 350) and (not trigger.admin):
        return bot.reply('La frase debe ser menor a 350 caracteres')

    src = args[0]
    dest = args[1]
    if src != dest:
        msg, src = translate(phrase, src, dest)
        if sys.version_info.major < 3 and isinstance(msg, str):
            msg = msg.decode('utf-8')
        if msg:
            msg = web.decode(msg)  # msg.replace('&#39;', "'")
            msg = '%s' % msg
        else:
            msg = 'La traducción de %s a %s ha fallado, lo siento!' % (src, dest)

        bot.reply(msg)
    else:
        bot.reply('La detección de idioma ha fallado, intenta sugerir uno!')

@commands('trb', 'bingt', 'microsofttranslator')
def trb(bot, trigger):
    """Traduce un texto instantaneamente usando el traductor de Bing"""
    if not trigger.group(2):
        return bot.reply('Para usar el traductor ingresa "%trb [idioma origen] [idioma destino] [texto a traducir]"')
    command = trigger.group(2).split(' ')
    from_lang = command[0]
    to_lang = command[1]
    text = ' '.join(command[2:])
    bot.reply(translate_bing(text, from_lang, to_lang, bot))
