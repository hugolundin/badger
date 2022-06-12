import logging; log = logging.getLogger(__name__)  # fmt: skip

import json

from mitmproxy import ctx, http, exceptions, addonmanager


class ProxyHandler:
    def __init__(self):
        self.mappings = {}

    def load(self, loader: addonmanager.Loader):
        loader.add_option(
            name="mappings",
            typespec=str,
            default=json.dumps({}),
            help="Mappings to use in proxy.",
        )

    def running(self):
        for mapping in json.loads(ctx.options.mappings):
            try:
                name = mapping["name"]
                host = mapping["host"]
                port = mapping["port"]
            except KeyError as e:
                raise exceptions.OptionsError(f"{e}")

            self.mappings[name] = (host, port)

    def request(self, flow: http.HTTPFlow):
        for name, destination in self.mappings.items():
            if flow.request.pretty_host == f"{name}.local":
                flow.request.host = destination[0]
                flow.request.port = destination[1]
                break


addons = [ProxyHandler()]
