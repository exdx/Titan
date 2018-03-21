#!/bin/bash

chgrp 101 $PWD || true
chmod g+w $PWD || true
chgrp 101 ./titan_app.py || true
chmod g+w ./titan_app.py || true


docker run -it --rm --publish 5555:5555 -v $PWD:/titan/src/Titan --name titan "$@" titan:latest
