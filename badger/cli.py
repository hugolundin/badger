import logging, coloredlogs
log = logging.getLogger(__name__)

import sys
import click
import asyncio
from signal import SIGINT, SIGTERM
from setproctitle import setproctitle

from .badger import Badger

def cancel():
    for t in asyncio.all_tasks():
        t.cancel()

@click.command()
@click.option('--level', type=click.Choice(coloredlogs.find_defined_levels().keys()), default='WARNING')
@click.pass_context
def main(ctx, level):
    coloredlogs.install(
        stream=sys.stdout,
        fmt='%(asctime)s %(levelname)s %(message)s',
        level=coloredlogs.find_defined_levels()[level])

    setproctitle(ctx.command_path)

    badger = Badger()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    for s in [SIGINT, SIGTERM]:
        loop.add_signal_handler(s, cancel)

    try:
       loop.run_until_complete(badger.run())
    except asyncio.exceptions.CancelledError:
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
