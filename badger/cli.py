import logging; log = logging.getLogger(__name__)  # fmt: skip

import sys
import asyncio

import click
import coloredlogs
from setproctitle import setproctitle
from click_extra.config import config_option

from .badger import Badger
from .utilities import exec, parse_mappings


@click.command(context_settings={"show_default": True})
@click.option("--mappings", multiple=True)
@click.option("--enable-docker/--disable-docker", is_flag=True, default=True)
@click.option(
    "--level",
    type=click.Choice(coloredlogs.find_defined_levels().keys()),
    default="WARNING",
)
@click.option("--external-logs/--no-external-logs", is_flag=True, default=False)
@click.pass_context
@config_option()
def badger(ctx, mappings, enable_docker, level, external_logs):
    coloredlogs.install(
        stream=sys.stdout,
        fmt="[%(name)s] %(asctime)s %(levelname)s %(message)s",
        level=coloredlogs.find_defined_levels()[level],
    )

    if not external_logs:
        for name, logger in logging.Logger.manager.loggerDict.items():
            if not name.startswith(ctx.command_path):
                logger.disabled = True

    badger = Badger(parse_mappings(mappings), enable_docker)

    setproctitle(ctx.command_path)
    exec(badger.run())
