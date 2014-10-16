# coding=utf8
"""
imdb.py - Willie Movie Information Module
Copyright © 2012-2013, Elad Alfassa, <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

This module relies on imdbapi.com
"""
from __future__ import unicode_literals
import json
import willie.web as web
import willie.module


@willie.module.commands('movie', 'imdb', 'pelicula')
@willie.module.example('%movie Detrás del último no hay nadie', '[PELICULA] Película no encontrada!')
@willie.module.example('.movie Citizen Kane', '[PELICULA] Title: Citizen Kane | Year: 1941 | Rating: 8.5 | Genre: Drama, Mystery | IMDB Link: http://imdb.com/title/tt0033467')
def movie(bot, trigger):
    """
    Devuelve información de una película como el título, año de publicación, genero, rating de IMDB
    """
    if not trigger.group(2):
        return
    word = trigger.group(2).rstrip()
    uri = "http://www.imdbapi.com/?t=" + word
    u = web.get(uri, 30)
    data = json.loads(u)  # data is a Dict containing all the information we need
    if data['Response'] == 'False':
        if 'Error' in data:
            message = '[PELICULA] %s' % data['Error']
        else:
            bot.debug(__file__, 'Se obtuvo un error de la API: %s' % word, 'warning')
            bot.debug(__file__, str(data), 'warning')
            message = '[PELICULA] Hubo un error en la Api de IMDB'
    else:
        message = '[PELICULA] Título: ' + data['Title'] + \
                  ' | Año: ' + data['Year'] + \
                  ' | Rating: ' + data['imdbRating'] + \
                  ' | Genero: ' + data['Genre'] + \
                  ' | Enlace a IMDB: http://imdb.com/title/' + data['imdbID']
    bot.say(message)


if __name__ == "__main__":
    from willie.test_tools import run_example_tests
    run_example_tests(__file__)
