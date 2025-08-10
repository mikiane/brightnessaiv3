#!/bin/bash
#!/bin/bash

# Lancement de Gunicorn avec la configuration spécifique
/home/michel/brightnessaiv3/env/bin/gunicorn --bind 0.0.0.0:8000 -w 4 streaming_api:app --timeout 1200 --daemon --access-logfile docs/access.log --error-logfile docs/error.log --capture-output

/home/michel/brightnessaiv3/env/bin/gunicorn --bind 0.0.0.0:8001 -w 4 transformers_api:app --timeout 7200 --daemon --access-logfile docs/access.log --error-logfile docs/error.log --capture-output

/home/michel/brightnessaiv3/env/bin/gunicorn --bind 0.0.0.0:8002 -w 4 alter_brain_api:app --timeout 1200 --daemon --access-logfile docs/access.log --error-logfile docs/error.log --capture-output

