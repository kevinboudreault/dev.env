ARG PHP_VERSION="8.3-fpm"
FROM php:${PHP_VERSION}

ARG PHP_XDEBUG_MODE=""
ARG USERNAME="laravel"
ARG GROUPNAME="laravel"
ARG UID=1000
ARG GID=1000
ARG TZ


RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd

COPY xdebug.config* /tmp/
RUN if [ "${PHP_XDEBUG_MODE}" = "debug" ]; then \
        if [ -f /tmp/xdebug.config ]; then \
            cat /tmp/xdebug.config >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini && rm /tmp/xdebug.config; \
        fi \
        && pecl install xdebug \
        && docker-php-ext-enable xdebug \
        && echo "xdebug.mode=debug" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini \
        && echo "xdebug.start_with_request=yes" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini \
        && echo "xdebug.client_host=host.docker.internal" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini \
        && echo "xdebug.client_port=9003" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini \
        && echo "xdebug.log=/var/log/xdebug.log" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini; \
    else \
        echo "Skipping Xdebug installation"; \
    fi

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# RUN curl -fsSL https://nodesource.com | bash - \
#     && apt-get install -y nodejs

# Use local node version
COPY --from=node:20 /usr/local/bin /usr/local/bin
COPY --from=node:20 /usr/local/lib/node_modules /usr/local/lib/node_modules

RUN groupadd -g ${GID} ${GROUPNAME} -f && \
    useradd -u ${UID} -g ${GID} -m ${USERNAME}

WORKDIR /var/www

USER ${USERNAME}

COPY . /var/www

EXPOSE 9000
CMD ["php-fpm"]