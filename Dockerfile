#
# I build with 
#   docker build . --tag titan:$(date +%F) --tag titan:latest
#
# Learn how to use volumes if you want your modifications in the container at runtime and not build time.
#
# Run with something like this for interactive
#  docker run -it --rm -p 5555:5555 -v $PWD/titan_app.py:/titan/src/Titan/titan_app.py titan:latest
#
# Run with something like this for background
#  docker run --restart=always -p 5555:5555 -v $PWD/titan_app.py:/titan/src/Titan/titan_app.py titan:latest
#
from python:3.6-alpine3.7

RUN apk --no-cache add \
    bash \
    curl \
    freetype \
    freetype-dev \
    g++ \
    gcc \
    gfortran \
    git \
    libpng \
    libpng-dev \
    libstdc++ \
    make \
    py3-gobject3 \
    py3-numpy \
    py3-cairo \
    py3-cairo-dev \
    py3-sqlalchemy \
    py3-tornado \
    py3-virtualenv \
    python3-dev \
    tzdata

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

RUN addgroup -S titan && adduser -S -G titan -s /bin/ash titan

RUN virtualenv /titan && chown -R titan:titan /titan

COPY entry.sh /entry.sh
RUN chmod +x /entry.sh

USER titan

WORKDIR /titan
RUN mkdir src
WORKDIR /titan/src
RUN git clone https://github.com/JustinHop/Titan.git
WORKDIR /titan/src/Titan
RUN source /titan/bin/activate && pip install -r requirements.txt


EXPOSE 5555
CMD /entry.sh
