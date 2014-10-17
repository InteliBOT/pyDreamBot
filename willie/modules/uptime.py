# coding=utf8
"""
uptime.py - Uptime module
Copyright 2014, Fabian Neundorf
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""
from __future__ import unicode_literals

from willie.module import commands
import datetime

def memoryusage():
    """Memory usage of the current process in kilobytes."""
    status = None 
    result = {'peak': 0, 'rss': 0, 'reads': 0}
    try:
        # This will only work on systems with a /proc file system
        # (like Linux).
        status = open('/proc/self/status')
        for line in status:
            parts = line.split()
            key = parts[0][2:-1].lower()
            if key in result:
                result[key] = int(parts[1])
    finally:
        if status is not None:
            status.close()
        print(result)
        return result

def setup(bot):
    if "uptime" not in bot.memory:
        bot.memory["uptime"] = datetime.datetime.utcnow()


@commands('uptime', 'status', 'estado')
def uptime(bot, trigger):
    """Devuelve información del estado de DreamBot"""
    delta = datetime.timedelta(seconds=round((datetime.datetime.utcnow() -
                                              bot.memory["uptime"])
                                             .total_seconds()))
    bot.reply("¡He estado aquí por {} y seguiré ejecutandome!".format(delta))

    x = memoryusage()
    rss = "\2" + str(round(int(x['rss']) / 1024, 1)) + "\2"
    peak = "\2" + str(round(int(x['peak']) / 1024, 1)) + "\2"
    threads = "\2" + str(x['reads']) + "\2"
    bot.reply("Memoria residente en uso: {0} MiB · Máximo: {1} MiB · Usando {2} hilos".format(rss, peak, threads))
