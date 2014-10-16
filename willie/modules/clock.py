# coding=utf8
"""
clock.py - Willie Clock Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Copyright 2012, Edward Powell, embolalia.net
Licensed under the Eiffel Forum License 2.

http://willie.dfbta.net
"""
from __future__ import unicode_literals

try:
    import pytz
except ImportError:
    pytz = None

import datetime
from willie.module import commands, example, OP
from willie.tools import get_timezone, format_time


def configure(config):
    config.interactive_add('clock', 'tz',
                           'Preferred time zone (http://dft.ba/-tz)', 'UTC')
    config.interactive_add('clock', 'time_format',
                           'Preferred time format (http://strftime.net)', '%F - %T%Z')


def setup(bot):
    #Having a db means pref's exists. Later, we can just use `if bot.db`.
    if bot.db and not bot.db.preferences.has_columns('tz'):
        bot.db.preferences.add_columns(['tz'])
    if bot.db and not bot.db.preferences.has_columns('time_format'):
        bot.db.preferences.add_columns(['time_format'])


@commands('t', 'time', 'hora')
@example('.t America/New_York')
def f_time(bot, trigger):
    """Da la hora actual en alguna zona horaria."""
    if trigger.group(2):
        zone = get_timezone(bot.db, bot.config, trigger.group(2).strip(), None, None)
        if not zone:
            bot.say('No se ha encontrado la zona horaria %s.' % trigger.group(2).strip())
            return
    else:
        zone = get_timezone(bot.db, bot.config, None, trigger.nick,
                            trigger.sender)
    time = format_time(bot.db, bot.config, zone, trigger.nick, trigger.sender)
    bot.say(time)


@commands('settz', 'timez')
@example('.settz America/New_York')
def update_user(bot, trigger):
    """
    Cambia tu zona horaria predeterminada. Ejemplos y más en: http://dft.ba/-tz
    """
    if not pytz:
        bot.reply("Lo siento, no tengo soporte para zonas horarias.")
    elif not bot.db:
        bot.reply("No puedo recordar eso, no tengo base de datos.")
    else:
        tz = trigger.group(2)
        if not tz:
            bot.reply("Que zona horaria uso? En el siguiente sitio hay varias "
                         "http://dft.ba/-tz")
            return
        if tz not in pytz.all_timezones:
            bot.reply("No conozco esa zona horaria, busca una en "
                         "http://dft.ba/-tz")
            return

        bot.db.preferences.update(trigger.nick, {'tz': tz})
        if len(tz) < 7:
            bot.say("Okay, " + trigger.nick +
                        ", pero necesito una zona horaria de http://dft.ba/-tz si "
                        "usas DST.")
        else:
            bot.reply('Ahora estás en la zona horaria %s, genial!' % tz)


@commands('settimeformat', 'settf', 'fzh', 'formatozonahoraria')
@example('.settf %FT%T%z')
def update_user_format(bot, trigger):
    """
    Establece el formato de fecha y hora de un usuario. Puedes buscar uno de tu preferencia en http://strftime.net o en
    cualquier motor de búsqueda.
    """
    if bot.db:
        tformat = trigger.group(2)
        if not tformat:
            bot.reply("Que formato de zona horaria deseas utilizar?"
                         " Entra a http://strftime.net para crear uno.")

        tz = get_timezone(bot.db, bot.config, None, None,
                                       trigger.sender)

        # Get old format as back-up
        old_format = bot.db.preferences.get(trigger.nick, 'time_format')

        # Save the new format in the database so we can test it.
        bot.db.preferences.update(trigger.nick, {'time_format': tformat})

        try:
            timef = format_time(db = bot.db, zone=tz, nick=trigger.nick)
        except:
            bot.reply("Ese formato no es válido. Entra a"
                         " http://strftime.net para crear uno.")
            # New format doesn't work. Revert save in database.
            bot.db.preferences.update(trigger.nick, {'time_format': old_format})
            return
        bot.reply("Fantástico!. Tu hora ahora se mostrará como %s. (Si tu "
                     "zona horaria es incorrecta, puedes cambiarla con el comando timez)"
                     % timef)
    else:
        bot.reply("No puedo recordar eso! no tengo base de datos :/")


@commands('channeltz')
@example('.chantz America/New_York')
def update_channel(bot, trigger):
    """
    Establece la zona horaria preferida para el canal
    """
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    elif not pytz:
        bot.reply("No tengo soporte para zonas horarias activado, lo siento.")
    elif not bot.db:
        bot.reply("No puedo recordar eso, no tengo base de datos.")
    else:
        tz = trigger.group(2)
        if not tz:
            bot.reply("Que zona horaria deseas establecer? Puedes buscar una en "
                         "http://dft.ba/-tz")
            return
        if tz not in pytz.all_timezones:
            bot.reply("No conozco esa zona horaria, busca una en "
                         "http://dft.ba/-tz")
            return

        bot.db.preferences.update(trigger.sender, {'tz': tz})
        if len(tz) < 7:
            bot.say("Okay, " + trigger.nick +
                        ", pero debes colocar una zona horaria de http://dft.ba/-tz si "
                        "usas DST.")
        else:
            bot.reply(
                'Ahora tengo a {} en la zona horaria {}.'.format(trigger.sender,tz))


@commands('setchanneltimeformat', 'setctf')
@example('setctf %FT%T%z')
def update_channel_format(bot, trigger):
    """
    Sets your preferred format for time. Uses the standard strftime format. You
    can use http://strftime.net or your favorite search engine to learn more.
    """
    if bot.privileges[trigger.sender][trigger.nick] < OP:
        return
    elif not bot.db:
        bot.reply("I can't remember that; I don't have a database.")
    else:
        tformat = trigger.group(2)
        if not tformat:
            bot.reply("What format do you want me to use? Try using"
                         " http://strftime.net to make one.")

        tz = get_timezone(bot.db, bot.config, None, None,
                                       trigger.sender)
        try:
            timef = format_time(zone=tz)
        except:
            bot.reply("That format doesn't work. Try using"
                         " http://strftime.net to make one.")
            return
        bot.db.preferences.update(trigger.sender, {'time_format': tformat})
        bot.reply("Got it. Times in this channel  will now appear as %s "
                     "unless a user has their own format set. (If the timezone"
                     " is wrong, you might try the settz and channeltz "
                     "commands)" % timef)

