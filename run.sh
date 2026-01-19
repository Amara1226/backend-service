export PYTHONPATH="$(pwd)/src"
export AETHER_CONFIG="config/server_config.json"
export AETHER_SENSORS="config/sensors.json"
python -m aether.run
