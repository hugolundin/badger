# badger

mDNS-based reverse proxy for naming services on a local network.

<br>
<img src="./docs/badger-dark.png#gh-dark-mode-only" style="width: 65%;">
<img src="./docs/badger-light.png#gh-light-mode-only" style="width: 65%;">

## Sample config

Configuration should be placed in `~/.badger/config.toml`, but this can be changed with `--config <path>`. The config can also be given as either `JSON`, `YAML`, `YML`, `INI` or `XML`.

```toml
[badger]
level="INFO" # Set default logging level to INFO.
enable_docker=false # Disable Docker support.

mappings = [
    "service1@10.0.0.3:5000", # Map service1.local -> 10.0.0.3:5000.
    "service2@10.0.0.50:80",  # Map service2.local -> 10.0.0.50:80.
    "service3@10.0.0.4:5256"  # Map service3.local -> 10.0.0.4:5256.
]
```
