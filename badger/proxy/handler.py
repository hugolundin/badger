import json

from mitmproxy import http, addonmanager, ctx, exceptions

# mitmdump -p 80 -s handler.py --quiet --set mappings='[{"name": "hej", "host": "127.0.0.1", "port": 8800}]'

class ProxyHandler:
    def __init__(self):
        self.mappings = {}

    def load(self, loader: addonmanager.Loader):
        loader.add_option(
            name='mappings',
            typespec=str,
            default='{}',
            help='Mappings to use in proxy.'            
        )

    def running(self):
        for mapping in json.loads(ctx.options.mappings):
            try:
                name = mapping['name']
                host = mapping['host']
                port = mapping['port']
            except KeyError as e:
                raise exceptions.OptionsError(f'{e}')

            self.mappings[name] = (host, port)

    def request(self, flow: http.HTTPFlow):
        for name, destination in self.mappings.items():
            if flow.request.pretty_host == f'{name}.local':
                flow.request.host = destination[0]
                flow.request.port = destination[1]
                break

addons = [ProxyHandler()]
