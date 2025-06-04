# AstroTracker

This repository contains utilities for astrological calculations.  Planet
interpretations are defined in `utils/planet_descriptions.py`.

## Updating Planet Descriptions

By default, descriptions are bundled with the code.  To override them with a
new set, provide a URL via the `PLANET_DESCRIPTION_URL` environment variable
pointing to a JSON object mapping planet names to description strings.  When the
module is imported it will attempt to download that file and merge any new
values.  A sample JSON file is located at `data/planet_descriptions.json`.

