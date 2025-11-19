# Official Dockware Image
# Copyright 2025 dasistweb GmbH
#
FROM ubuntu:24.04
LABEL title="Dockware image for Shopware" \
      maintainer="dasistweb GmbH"

ARG VERSION
ARG MIN_PHP

## ***********************************************************************
##  IMAGE VARIABLES
## ***********************************************************************
ENV TZ=Europe/Berlin
ENV PHP_VERSION=not-set
ENV NODE_VERSION=not-set
ENV APACHE_DOCROOT=/var/www/html/public
ENV SHOP_DOMAIN localhost
ENV RECOVERY_MODE=0
ENV SSH_USER=not-set
ENV SSH_PWD=not-set
ENV XDEBUG_REMOTE_HOST="host.docker.internal"
ENV XDEBUG_CONFIG="idekey=PHPSTORM"
ENV PHP_IDE_CONFIG="serverName=localhost"
ENV XDEBUG_ENABLED=0
ENV FILEBEAT_ENABLED=0
ENV SUPERVISOR_ENABLED=0
ENV TIDEWAYS_KEY=not-set
ENV SW_CURRENCY 'not-set'
ENV SW_API_ACCESS_KEY 'not-set'
ENV SW_TASKS_ENABLED 0
ENV BASH_ENV=/var/www/.bashrc
ENV DEBIAN_FRONTEND=noninteractive


# these are all our files that we need to setup the image
COPY --chmod=0755 ./scripts /dockware/tmp/scripts
COPY --chmod=0755 ./config /dockware/tmp/config
# this are runtime executables for users
COPY --chmod=0755 ./assets/makefile /var/www/makefile
COPY --chmod=0755 ./assets/scripts /var/www/scripts
# entrypoint
COPY --chmod=0755 entrypoint.sh /entrypoint.sh

# -------------------------------------------------------------------------------------------------------

# these are identifier values
# that are read and shown to the user about this image
RUN echo "1:env-variables" && \
    mkdir -p /dockware && \
    echo "${VERSION}" > /dockware/version.txt && \
    echo "${MIN_PHP}" > /dockware/min_php.txt && \
    date >/dockware/build-date.txt && \
    echo "$(date +%Y) dasistweb GmbH" > /dockware/copyright.txt && \
    mkdir -p /var/www && \
    mkdir -p /var/www/scripts && \
    mkdir -p /var/dockware/cache && \
    echo "export TZ=${TZ}" >> /etc/profile && \
    echo "export PHP_VERSION=${PHP_VERSION}" >> /etc/profile && \
    echo "export APACHE_DOCROOT=${APACHE_DOCROOT}" >> /etc/profile && \
    echo "export SHOP_DOMAIN=${SHOP_DOMAIN}" >> /etc/profile && \
    echo "export NODE_VERSION=${NODE_VERSION}" >> /etc/profile && \
    echo "export RECOVERY_MODE=${RECOVERY_MODE}" >> /etc/profile && \
    echo "export SSH_USER=${SSH_USER}" >> /etc/profile && \
    echo "export SSH_PWD=${SSH_PWD}" >> /etc/profile && \
    echo "export XDEBUG_ENABLED=${XDEBUG_ENABLED}" >> /etc/profile && \
    echo "export XDEBUG_REMOTE_HOST=${XDEBUG_REMOTE_HOST}" >> /etc/profile && \
    echo "export XDEBUG_CONFIG=${XDEBUG_CONFIG}" >> /etc/profile && \
    echo "export PHP_IDE_CONFIG=${PHP_IDE_CONFIG}" >> /etc/profile && \
    echo "export FILEBEAT_ENABLED=${FILEBEAT_ENABLED}" >> /etc/profile && \
    echo "export SUPERVISOR_ENABLED=${SUPERVISOR_ENABLED}" >> /etc/profile && \
    echo "export SW_CURRENCY=${SW_CURRENCY}" >> /etc/profile && \
    echo "export SW_API_ACCESS_KEY=${SW_API_ACCESS_KEY}" >> /etc/profile && \
    echo "export SW_TASKS_ENABLED=${SW_TASKS_ENABLED}" >> /etc/profile && \
    echo "export TIDEWAYS_KEY=${TIDEWAYS_KEY}" >> /etc/profile

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##  BASE REQUIREMENTS
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
RUN echo "2:basics" && \
    apt-get update && \
    # first install tools to add repositories
    apt-get install -y wget gnupg2 sudo apt-transport-https software-properties-common && \
    LC_ALL=C.UTF-8 add-apt-repository ppa:ondrej/php && \
    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add - && \
    echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-7.x.list && \
    sudo echo 'deb [signed-by=/usr/share/keyrings/tideways.gpg] https://packages.tideways.com/apt-packages-main any-version main' | sudo tee /etc/apt/sources.list.d/tideways.list && \
    wget -qO - 'https://packages.tideways.com/key.gpg' | gpg --dearmor | sudo tee /usr/share/keyrings/tideways.gpg > /dev/null && \
    # update our repositories
    apt-get update && \
    # make mysql installation non-interactive ;)
    echo debconf mysql-server/root_password password root | debconf-set-selections && \
    echo debconf mysql-server/root_password_again password root | debconf-set-selections && \
    # now have fun installing stuff
    apt-get install -y --no-install-recommends \
            gosu \
            make \
            curl \
            tzdata \
            vim \
            unzip \
            bzip2 \
            zstd \
            ssmtp \
            lsof \
            openssh-server openssl sshpass \
            cron \
            jq \
            gpg-agent \
            rsync \
            supervisor \
            jpegoptim \
            git git-lfs patch \
            apache2 libapache2-mod-fcgid  \
            tideways-php tideways-daemon \
            mysql-server-8.0 mysql-client \
            filebeat \
            ruby ruby-dev build-essential && \
    gem install mailcatcher && \
    apt-get remove -y ruby-dev build-essential && \
    mkdir /var/run/sshd && \
    ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime && echo "${TZ}" > /etc/timezone && \
    # --------------------------------------------------------------------------- \
    mkdir -p /var/www/pimpmylog && \
    wget -O - https://github.com/potsky/PimpMyLog/tarball/master | tar xzf - && \
    mv potsky-PimpMyLog-* /var/www/pimpmylog && \
    mv /var/www/pimpmylog/potsky-PimpMyLog-2fed8c1/* /var/www/pimpmylog && \
    rm -rf /var/www/pimpmylog/potsky-PimpMyLog-* && \
    mv /dockware/tmp/config/pimpmylog/config.user.d /var/www/pimpmylog/config.user.d && \
    mv /dockware/tmp/config/pimpmylog/config.user.json /var/www/pimpmylog/config.user.json && \
    # apply our custom file with fixes for PHP 8
    # its used from here: https://github.com/potsky/PimpMyLog/pull/149/files
    mv /dockware/tmp/config/pimpmylog/global.inc.php /var/www/pimpmylog/inc/global.inc.php && \
    chown -R www-data:www-data /var/www/pimpmylog/ && \
    # --------------------------------------------------------------------------
    # configure ssmtp to use local mailcatcher
    sed -i 's/^mailhub=mail$/mailhub=localhost:1025/' /etc/ssmtp/ssmtp.conf && \
    # ---------------------------------------------------------------------------
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##  USER MANAGEMENT
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
RUN echo "3:users" && \
    echo "root:root" | chpasswd \
    # set password for www-data, and also
    # avoid shell login (we have a separate user for that)
    echo 'www-data:www-data' | chpasswd && \
    usermod -s /usr/sbin/nologin www-data && \
    # this option makes sure to avoid root SSH login
    # we just replace our lines with nothing
    sed -i 's/PermitRootLogin without-password//' /etc/ssh/sshd_config && \
    sed -i 's/PermitRootLogin prohibit-password//' /etc/ssh/sshd_config && \
    # allow root and sudo group to run sudo without password
    sed -i /etc/sudoers -re 's/^%sudo.*/%sudo ALL=(ALL:ALL) NOPASSWD: ALL/g' && \
    sed -i /etc/sudoers -re 's/^root.*/root ALL=(ALL:ALL) NOPASSWD: ALL/g'  &&\
    # remove include directory
    sed -i /etc/sudoers -re 's/^#includedir.*/## **Removed the include directive** ##"/g' && \
    # add our dockware user
    adduser --disabled-password --uid 5577 --gecos "" --ingroup www-data dockware && \
    usermod -m -d /var/www dockware | true && \
    echo "dockware:dockware" | chpasswd && \
    usermod -a -G sudo dockware && \
    # allow sudo without pwd and dont require tty (for entrypoint commands)
    echo "Defaults:dockware !requiretty" >> /etc/sudoers && \
    sed -i 's/dockware:x:5577:33:/dockware:x:33:33:/g' /etc/passwd && \
    echo 'AllowUsers dockware' >> /etc/ssh/sshd_config && \
    # create a new id_rsa for the www-data dockeruser.
    # thus we have a SSH Key for connections out of the box
    mkdir -p /var/www/.ssh && \
    rm -rf /var/www/.ssh/id_rsa; true && \
    rm -rf /var/www/.ssh/id_rsa.pub; true && \
    ssh-keygen -t rsa -b 4096 -f /var/www/.ssh/id_rsa -C "Dockware Container" -P "" && \
    chown -R www-data:www-data /var/www/.ssh && \
    chmod 0700 /var/www/.ssh && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##  APACHE + MYSQL CONFIGURATION
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
RUN echo "4:apache-mysql" && \
    cp /dockware/tmp/config/apache/http2.conf /etc/apache2/conf-available/http2.conf && \
    cp /dockware/tmp/config/apache/apache2.conf /etc/apache2/apache2.conf && \
    cp /dockware/tmp/config/apache/ports.conf /etc/apache2/ports.conf && \
    cp /dockware/tmp/config/apache/sites.conf /etc/apache2/sites-enabled/000-default.conf && \
    a2enmod headers rewrite expires proxy proxy_http proxy_wstunnel actions fcgid alias proxy_fcgi http2 ssl && \
    sudo a2enconf http2 && \
    sudo a2dismod mpm_prefork > /dev/null 2>&1 && \
    sudo a2enmod mpm_event > /dev/null 2>&1 && \
    # remove the standard apache index file
    mkdir -p /var/www/html && \
    rm -rf /var/www/html/* && \
    chown -R www-data:www-data /var/www/html && \
    sudo -u www-data sh -c 'mkdir -p /var/www/html/public'  && \
    # make sure the configured log folder exists and is writeable
    chmod -R 0777 /var/www && \
    chgrp -R www-data /var/log/apache2 && \
    mkdir -p /var/log/mysql && \
    chgrp -R www-data /var/log/mysql &&\
    mkdir /var/log/php -p  && \
    touch /var/log/php/cli_errors.log && \
    touch /var/log/php/fpm_errors.log && \
    chown -R www-data:www-data /var/log/php && \
    chmod 0755 /var/log/php && \
    ## ***********************************************************************
    ##  MOD_SSL
    ##  create SSL certificate
    ## ***********************************************************************
    mkdir /etc/apache2/ssl && \
    openssl req -new -x509 -days 365 -sha1 -newkey rsa:2048 -nodes -keyout /etc/apache2/ssl/server.key -out /etc/apache2/ssl/server.crt -subj '/O=Company/OU=Department/CN=localhost' && \
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    cp /dockware/tmp/config/mysql/my.cnf /etc/mysql/my.cnf && \
    # -------------------------------------
    usermod -d /var/lib/mysql/ mysql  && \
    sudo chmod -R 750 /var/lib/mysql && \
    # -------------------------------------
    service mysql start && \
    # create either user for % and also localhost as otherwise you could have to connect to 127.0.0.1 and not localhost as mysql treats this different
    sudo mysql --user=root --password=root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';FLUSH PRIVILEGES;use mysql;select user from user;" && \
    sudo mysql --user=root --password=root -e "CREATE USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'root';GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;FLUSH PRIVILEGES;use mysql;select user from user;" && \
    # -------------------------------------
    service mysql stop && \
    # -------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------- \
    mkdir /var/www/adminer && \
    wget "https://github.com/adminerevo/adminerevo/releases/download/v4.8.4/adminer-4.8.4.php" -O /var/www/adminer/index.php && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##  PHP INSTALLATION
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
RUN echo "6:php" && \
    sudo apt-get update && \
    cd /dockware/tmp/scripts && bash install_php.sh && \
    curl -sS https://getcomposer.org/installer | php -- --install-dir=/tmp --version=2.2.9 --quiet && \
    # prepare "global" composer directory for www-data
    mkdir -p /var/www/.composer && \
    export COMPOSER_HOME="/var/www/.composer" && \
    chmod 755 /tmp/composer.phar && \
    mv /tmp/composer.phar /usr/local/bin/composer && \
    chown -R 33:33 /var/www/.composer && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


## ***********************************************************************
##  NODE INSTALLATION
## ***********************************************************************
RUN echo "7:node" && \
    cd /dockware/tmp/scripts && bash install_node.sh && \
    mkdir /var/www/.npm && \
    npm config set cache /var/www/.npm && \
    chown 33:33 -R /var/www/.npm && \
    tar -cf - -C /var/www/.nvm . | zstd --ultra -22 -o /var/www/nvm.tar.zst && \
    rm -rf /var/www/.nvm/* && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


## ***********************************************************************
##  SHOPWARE INSTALLATION
## ***********************************************************************
RUN echo "8:shopware" && \
    SW_VERSION=$(cat /dockware/version.txt) && \
    SW_MIN_PHP=$(cat /dockware/min_php.txt) && \
    if [ "$SW_VERSION" != "none" ]; then \
        cd /dockware/tmp/scripts && bash install_shopware.sh $SW_VERSION $SW_MIN_PHP && \
        tar -cf - -C /var/www/html . | zstd --ultra -22 -o /var/www/shopware.tar.zst && \
        find /var/www/html -mindepth 1 -delete && \
        # we need the zst in the html folder. if existing entrypoint.sh will decompress it \
        # it has to be in html, because users might mount that folder, and if its not inside, it would \
        # always exist and therefore always overwrite the users custom-mount html folder \
        mv /var/www/shopware.tar.zst /var/www/html/shopware.tar.zst; \
    fi; \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \

## ***********************************************************************
##  PERMISSIONS
## ***********************************************************************
    echo "9:permissions+cleanup" && \
    chown 33:33 -R /var/www/scripts && \
    chown 33:33 -R /var/www/html && \
    rm -rf /dockware/tmp && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

## ***********************************************************************
## SWITCH TO NORMAL USER (NOT ROOT ANYMORE!)
## everything down here is now done as our www-data / dockware user
## just like you would do it manually in the container
## ***********************************************************************

USER dockware

# make the apache folder the working directory
WORKDIR /var/www/html

## ***********************************************************************
##  POST BUILD
## ***********************************************************************

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]

HEALTHCHECK --interval=5s --timeout=3s --retries=10 CMD [ "sh", "-c", "test -f /var/www/container.launched" ]