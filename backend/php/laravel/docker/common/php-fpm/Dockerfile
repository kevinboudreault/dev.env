FROM production AS development

ARG PHP_XDEBUG_ENABLED=true
ARG PHP_XDEBUG_MODE=develop,coverage,debug,profile
ARG PHP_XDEBUG_HOST=host.docker.internal
ARG PHP_XDEBUG_IDE_KEY=DOCKER
ARG PHP_XDEBUG_LOG=/dev/stdout
ARG PHP_XDEBUG_LOG_LEVEL=0

USER root

RUN if [ "${PHP_XDEBUG_ENABLED}" = "true" ]; then \
    pecl install xdebug && \
    docker-php-ext-enable xdebug && \
    echo "xdebug.mode=${PHP_XDEBUG_MODE}" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini && \
    echo "xdebug.idekey=${PHP_XDEBUG_IDE_KEY}" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini && \
    echo "xdebug.log=${PHP_XDEBUG_LOG}" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini && \
    echo "xdebug.log_level=${PHP_XDEBUG_LOG_LEVEL}" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini && \
    echo "xdebug.client_host=${PHP_XDEBUG_HOST}" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini ; \
    echo "xdebug.start_with_request=yes" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini ; \
fi

ARG UID=1000
ARG GID=1000

RUN if getent group ${GID}; then \
      group_name=$(getent group ${GID} | cut -d: -f1); \
      useradd -m -u ${UID} -g ${GID} -s /bin/bash www; \
    else \
      groupadd -g ${GID} www && \
      useradd -m -u ${UID} -g www -s /bin/bash www; \
      group_name=www; \
    fi

RUN sed -i "s/user = www-data/user = www/g" /usr/local/etc/php-fpm.d/www.conf && \
    sed -i "s/group = www-data/group = $group_name/g" /usr/local/etc/php-fpm.d/www.conf

WORKDIR /var/www

COPY ./docker/dev/php-fpm/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER www-data

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

EXPOSE 9000
CMD ["php-fpm"]