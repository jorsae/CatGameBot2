import main
import discord
import math
from datetime import datetime, timedelta
import constants
import utility

def next(ctx, settings, iterations):
    iterations = utility.clean_iterations(iterations)

    if utility.is_event(settings) is False:
        next_event = utility.get_next_event(settings)
        embed = discord.Embed(colour=discord.Colour.red())

        if next_event is None:
            embed.set_author(name='No event is currently running.')
            return embed
        time_left = next_event - datetime.utcnow()
        embed.set_author(name=f'No event is currently running.\nNext event in {time_left}')
        return embed
    
    difference = (datetime.utcnow() - settings.start_time).total_seconds()
    event_iterations = math.floor(difference / constants.SIX_HOURS)
    next_event = (settings.start_event + event_iterations) % 3

    time_difference = constants.SIX_HOURS - (difference % constants.SIX_HOURS)
    
    embed = discord.Embed(colour=discord.Colour.green())
    embed.set_author(name=f'Next {iterations} event(s)')
    
    # Event is currently ongoing NOW
    if (constants.SIX_HOURS - time_difference) < 1800:
        time_left = constants.EVENT_DURATION - (constants.SIX_HOURS - time_difference)
        time_left = utility.format_timedelta(timedelta(seconds=time_left))
        embed.add_field(name=f'{constants.EVENTS[next_event]}', value=f'Running now! Time left: {time_left}')
        iterations -= 1
    
    for i in range(iterations):
        time_left = i * constants.SIX_HOURS + time_difference
        time_left = utility.format_timedelta(timedelta(seconds=time_left))
        event = (next_event + (i+1)) % 3
        embed.add_field(name=f'{constants.EVENTS[event]}', value=f'Time left: {time_left}')

    return embed

def list_events(ctx, settings):
    embed = discord.Embed(colour=discord.Colour.green())
    embed.set_author(name=f'Current events [utc]')

    for event in settings.event_times:
        embed.add_field(name='Mini event', value=f'{event.start_time} - {event.end_time}', inline=False)
    return embed

def stop(ctx, settings):
    author = str(ctx.message.author)
    is_admin = utility.is_admin(author, settings)
    if is_admin is False:
        logging.warning(f'stop was attempted to be executed by: {author}')
        return 'You do not have the permissions for this command'
    
    settings.run_ping_reminder = False
    return 'Ping reminder stopped successfully'

def start(ctx, settings, bot):
    author = str(ctx.message.author)
    is_admin = utility.is_admin(author, settings)
    if is_admin is False:
        logging.warning(f'start was attempted to be executed by: {author}')
        return 'You do not have the permissions for this command'
    
    settings.run_ping_reminder = True
    if settings.is_running_ping_reminder is False:
        bot.loop.create_task(ping_reminder())
        return 'Bot was started successfully | 1'
    
    return 'Bot was started successfully | 2'

def help(ctx, settings, bot):
    author = ctx.message.author
    display_hidden_commands = utility.is_admin(author, settings)

    embed = discord.Embed(colour=discord.Colour.orange())
    embed.set_author(name=f'CatGameBot Help')
    last_command = None
    for command in bot.walk_commands():
        command = bot.get_command(str(command))
        if command is None:
            continue
        if command.hidden is False or display_hidden_commands:
            if last_command != str(command):
                embed.add_field(name=f'{constants.PREFIX}{command}', value=command.help, inline=False)
            last_command = str(command)
    return embed