#!/bin/bash

SHOPWARE_VERSION=$1

if [ -z "$SHOPWARE_VERSION" ]; then
    echo "Usage: $0 <shopware-version>"
    exit 1
fi


sudo service mysql start
# -------------------------------------------------------------------------------------------
rm -rf /var/www/html
cd /var/www && composer create-project shopware/production:"$SHOPWARE_VERSION" --no-interaction --no-cache --no-dev html
cd /var/www/html && composer require --dev shopware/dev-tools
# -------------------------------------------------------------------------------------------
# ALWAYS UPDATE .env itself
# if we would use .env.local, then these things could happen....our 127.0.0.1 instead of localhost for MySQL might not exist in a users custom .env.local
# which would use Shopware default with localhost, which breaks the DB connection in MySQL 8
sed -i "/APP_ENV=/g" /var/www/html/.env
sed -i "/APP_URL=/g" /var/www/html/.env
sed -i "/DATABASE_URL=/g" /var/www/html/.env
sed -i "/MAILER_URL=/g" /var/www/html/.env
echo "APP_ENV=dev" >> /var/www/html/.env
echo "APP_URL=http://localhost" >> /var/www/html/.env
echo "DATABASE_URL=mysql://root:root@127.0.0.1:3306/shopware" >> /var/www/html/.env
echo "MAILER_DSN=smtp://127.0.0.1:1025" >> /var/www/html/.env
# -------------------------------------------------------------------------------------------
cd /var/www/html && php bin/console system:install --create-database --basic-setup
cd /var/www/html && php bin/console assets:install
# -------------------------------------------------------------------------------------------
mv /dockware/tmp/config/DockwareSamplePlugin /var/www/html/custom/plugins/DockwareSamplePlugin
cd /var/www/html && APP_ENV=prod php bin/console store:download -p SwagPlatformDemoData
cd /var/www/html && APP_ENV=prod php bin/console plugin:refresh
cd /var/www/html && APP_ENV=prod php bin/console plugin:install --activate SwagPlatformDemoData
cd /var/www/html && APP_ENV=prod php bin/console plugin:install --activate DockwareSamplePlugin
# -------------------------------------------------------------------------------------------
# clear cache and refresh dal index to show the new demo data
cd /var/www/html && php bin/console cache:clear
cd /var/www/html/bin && ./build-storefront.sh
cd /var/www/html && php bin/console theme:change --all --no-compile --no-interaction Storefront
cd /var/www/html && php bin/console theme:compile
cd /var/www/html && php bin/console dal:refresh:index
rm -rf /var/www/html/var/cache/*
# -------------------------------------------------------------------------------------------
mysql --host=127.0.0.1 --user=root --password=root -e "use shopware; INSERT INTO system_config (id, configuration_key, configuration_value, sales_channel_id, created_at, updated_at) VALUES (X'b3ae4d7111114377af9480c4a0911111', 'core.frw.completedAt', '{\"_value\": \"2019-10-07T10:46:23+00:00\"}', NULL, '2019-10-07 10:46:23.169', NULL);"
# -------------------------------------------------------------------------------------------
sudo service mysql stop