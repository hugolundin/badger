import logging, coloredlogs
log = logging.getLogger(__name__)

import sys
import click
import asyncio
import pathlib
from signal import SIGINT, SIGTERM
from setproctitle import setproctitle

from .badger import Badger

def cancel():
    for t in asyncio.all_tasks():
        t.cancel()

DEFAULT_CONFIG = 'config.toml'

@click.command()
@click.option("--config", type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--docker/--no-docker', default=True)
@click.option('--level', type=click.Choice(coloredlogs.find_defined_levels().keys()), default='WARNING')
@click.option('--external-logs', is_flag=True, default=False)
@click.pass_context
def main(ctx, config, docker, level, external_logs):
    coloredlogs.install(
        stream=sys.stdout,
        fmt='[%(name)s] %(asctime)s %(levelname)s %(message)s',
        level=coloredlogs.find_defined_levels()[level])

    if not external_logs:
        for name, logger in logging.Logger.manager.loggerDict.items():
            if not name.startswith(ctx.command_path):
                logger.disabled = True

    path = pathlib.Path(__file__).parent.with_name(config if config else DEFAULT_CONFIG).resolve()
    badger = Badger(path, docker)
    setproctitle(ctx.command_path)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for s in [SIGINT, SIGTERM]:
        loop.add_signal_handler(s, cancel)

    try:
       loop.run_until_complete(badger.run())
    except asyncio.exceptions.CancelledError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
