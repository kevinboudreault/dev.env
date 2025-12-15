ARG PHP_VERSION="8.2-fpm"
FROM php:${PHP_VERSION}

ARG PHP_XDEBUG_MODE
ARG USERNAME="symfony"
ARG GROUPNAME="symfony"
ARG UID=1000
ARG GID=1000
ARG TZ



RUN echo ${TZ} > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    libxml2-dev \
    libzip-dev \
    git \
    unzip

RUN docker-php-ext-configure gd --with-jpeg --with-freetype && docker-php-ext-install gd pdo pdo_mysql opcache zip

# Composer install
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Symfony install (latest version)
RUN curl -sS https://get.symfony.com/cli/installer | bash && \
    mv /root/.symfony*/bin/symfony /usr/local/bin/symfony

# Comment out xdebug install and configuration upload for production
RUN pecl install xdebug && \
    docker-php-ext-enable xdebug

# Upload Xdebug configuration file
COPY xdebug.config* /tmp/
RUN if [ "${PHP_XDEBUG_MODE}" = "debug" ]; then \
    cat /tmp/xdebug.config >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini && rm /tmp/xdebug.config; \
fi

# Comment out user and group directives in www.conf to avoid startup notices
RUN sed -i -e 's/^user = .*/;user = symfony/' -e 's/^group = .*/;group = symfony/' /usr/local/etc/php-fpm.d/www.conf

# Create new user with permission
RUN groupadd -g ${GID} ${GROUPNAME} -f && \
    useradd -u ${UID} -g ${GID} -m ${USERNAME}

WORKDIR /var/www

USER ${USERNAME}

CMD ["php-fpm"]