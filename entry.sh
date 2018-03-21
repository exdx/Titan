#!/bin/sh

cd /titan
source bin/activate

sed -e 's/app.run(port=5555)/app.run(host="0.0.0.0", port=5555)/' -i /titan/src/Titan/titan_app.py

python /titan/src/Titan/titan_app.py "$@"
