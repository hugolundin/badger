import sys
import asyncio
from signal import SIGINT, SIGTERM

import click
import coloredlogs
from setproctitle import setproctitle
from click_extra.config import config_option

from .badger import Badger

import logging; log = logging.getLogger(__name__)  # fmt: skip


def cancel():
    for t in asyncio.all_tasks():
        t.cancel()


@click.group(context_settings={"show_default": True})
@click.option(
    "--level",
    type=click.Choice(coloredlogs.find_defined_levels().keys()),
    default="WARNING",
)
@click.option("--external-logs", is_flag=True, default=False)
@click.pass_context
@config_option()
def badger(ctx, level, external_logs):
    coloredlogs.install(
        stream=sys.stdout,
        fmt="[%(name)s] %(asctime)s %(levelname)s %(message)s",
        level=coloredlogs.find_defined_levels()[level],
    )

    if not external_logs:
        for name, logger in logging.Logger.manager.loggerDict.items():
            if not name.startswith(ctx.command_path):
                logger.disabled = True


def parse_mappings(mappings) -> dict:
    result = {}

    for mapping in mappings:
        name, address = mapping.split("@")
        host, port = address.split(":")
        result[name] = (host, port)

    return result


@badger.command()
@click.option("--mappings", multiple=True)
@click.option("--enable-docker/--disable-docker", is_flag=True, default=True)
@click.pass_context
def run(ctx, mappings, enable_docker):
    badger = Badger(parse_mappings(mappings), enable_docker)
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
