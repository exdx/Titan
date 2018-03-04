from python:3.6-alpine3.7

ENV LANG C.UTF-8

RUN apk --no-cache add --upgrade \
    bash \
    curl \
    freetype \
    git \
    libpng \
    libstdc++ \
    postgresql-client \
    py3-gobject3 \
    py3-numpy \
    py3-cairo \
    py3-sqlalchemy \
    py3-tornado \
    py3-virtualenv \
    tzdata

RUN apk --no-cache add --virtual .build-deps \
    freetype-dev \
    g++ \
    gcc \
    gfortran \
    libpng-dev \
    make \
    py3-cairo-dev \
    py-numpy-dev \
    python3-dev

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

RUN addgroup -S titan && adduser -S -G titan -s /bin/bash titan
RUN virtualenv --system-site-packages /titan && chown -R titan:titan /titan

COPY entry.sh /entry.sh
RUN chmod +x /entry.sh

USER titan
WORKDIR /titan
RUN mkdir src
WORKDIR /titan/src
RUN git clone https://github.com/JustinHop/Titan.git
WORKDIR /titan/src/Titan
RUN source /titan/bin/activate && pip install -r requirements.txt && pip install Flask-SQLAlchemy

USER root
RUN apk del .build-deps

USER titan

EXPOSE 5555
CMD /entry.sh
