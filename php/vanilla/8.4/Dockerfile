FROM php:8.4-cli

ARG UID=1000
ARG GID=1000

# Dependencies
RUN echo "force-unsafe-io" > etc/dpkg/dpkg.cfg.d/02apt-speedup \
    && echo "Acquire::http {No-Cache=True;};" > /etc/apt/apt.conf.d/no-cache \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends --quiet \
        apt-transport-https curl git gnupg msmtp-mta mariadb-client openssh-client rsync unzip wget \
    && rm -rf /var/lib/apt/lists/*

# Extensions
RUN extensions="amqp apcu ast bcmath bitset brotli bz2 calendar csv dba decimal ds enchant ev event excimer exif ffi ftp gd gearman gettext gmp gnupg grpc http igbinary imagick imap inotify intl json_post jsonpath ldap luasandbox lz4 lzf mailparse maxminddb md4c memcache memcached memprof mongodb msgpack mysqli oauth odbc opcache opentelemetry parle pcntl pcov pdo_dblib pdo_firebird pdo_mysql pdo_odbc pdo_pgsql pdo_sqlsrv pgsql php_trie pkcs11 pq protobuf pspell psr raphf rdkafka redis saxon seasclick shmop simdjson smbclient snappy snmp soap sockets solr spx sqlsrv ssh2 stomp sync sysvmsg sysvsem sysvshm tideways tidy timezonedb uploadprogress uuid uv vips wikidiff2 xdebug xhprof xlswriter xmldiff xmlrpc xpass xsl yac yaml yar zephir_parser zip zmq zookeeper zstd" \
    && curl -sSLf -o /usr/local/bin/install-php-extensions https://github.com/mlocati/docker-php-extension-installer/releases/latest/download/install-php-extensions \
    && chmod +x /usr/local/bin/install-php-extensions \
    && install-php-extensions $extensions \
    && for ext in $extensions; do rm -f /usr/local/etc/php/conf.d/*php-ext-$ext.ini; done

# Composer    
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
    && apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# PHPUnit
RUN curl -sSLo phpunit.phar https://phar.phpunit.de/phpunit.phar \
    && chmod 755 phpunit.phar \
    && mv phpunit.phar /usr/local/bin/ \
    && ln -s /usr/local/bin/phpunit.phar /usr/local/bin/phpunit

# PHP Code Sniffer
RUN curl -OL https://squizlabs.github.io/PHP_CodeSniffer/phpcs.phar \
    && chmod 755 phpcs.phar \
    && mv phpcs.phar /usr/local/bin/ \
    && ln -s /usr/local/bin/phpcs.phar /usr/local/bin/phpcs \
    && curl -OL https://squizlabs.github.io/PHP_CodeSniffer/phpcbf.phar \
    && chmod 755 phpcbf.phar \
    && mv phpcbf.phar /usr/local/bin/ \
    && ln -s /usr/local/bin/phpcbf.phar /usr/local/bin/phpcbf

# XDebug config
ARG PHP_XDEBUG_ENABLED
ARG PHP_XDEBUG_MODE
ARG PHP_XDEBUG_HOST
ARG PHP_XDEBUG_LOG
ARG PHP_XDEBUG_LOG_LEVEL
ENV XDEBUG_VERSION=3.4.0

RUN if [ "${PHP_XDEBUG_ENABLED}" = "true" ]; then \
    curl -L https://xdebug.org/files/xdebug-$XDEBUG_VERSION.tgz | tar -zxf - \
    mv xdebug-$XDEBUG_VERSION xdebug && \
    pecl install xdebug-$XDEBUG_VERSION && \
    docker-php-ext-enable xdebug && \
    echo "xdebug.mode=${PHP_XDEBUG_MODE}" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini && \
    echo "xdebug.log=${PHP_XDEBUG_LOG}" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini && \
    echo "xdebug.log_level=${PHP_XDEBUG_LOG_LEVEL}" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini && \
    echo "xdebug.client_host=${PHP_XDEBUG_HOST}" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini ; \
    echo "xdebug.start_with_request=yes" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini ; \
fi

#Cleanup
RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false -o APT::AutoRemove::SuggestsImportant=false \
        apt-transport-https curl git gnupg msmtp-mta mariadb-client openssh-client rsync unzip wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Folder permission set
RUN if getent group ${GID}; then \
      useradd -m -u ${UID} -g ${GID} -s /bin/bash www; \
    else \
      groupadd -g ${GID} www && \
      useradd -m -u ${UID} -g www -s /bin/bash www; \
    fi && \
    usermod -aG sudo www && \
    echo 'www ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER www

COPY . /usr/src/myapp
COPY msmtprc /etc/

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

WORKDIR /usr/src/myapp

CMD ["php", "-a"]