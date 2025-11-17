#!/bin/bash

# we always support the 2 latest LTS versions
# https://nodejs.org/en/about/previous-releases
NODE_VERSIONS=("20" "22")

DEFAULT_NODE_VERSION=22


# -----------------------------------------------------------------------------------------
# INSTALL NVM
mkdir "/var/www/.nvm"
export NVM_DIR="/var/www/.nvm"
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# -----------------------------------------------------------------------------------------
# INSTALL NODE VERSIONS
for version in "${NODE_VERSIONS[@]}"; do
  nvm install "$version" -b
  nvm use "$version"
  # we have to install yarn in additional node versions
  # otherwise it won't be found after a nvm switch
  # npm install -g yarn
done

# -----------------------------------------------------------------------------------------
# "sudo node -v" also needs to work, so to a symlink with sudo
sudo ln -s "$(which node)" "/usr/local/bin/node"
sudo ln -s "$(which npm)" "/usr/local/bin/npm"

# -----------------------------------------------------------------------------------------
# SWITCH TO DEFAULT NODE VERSION
nvm use $DEFAULT_NODE_VERSION
nvm alias default $DEFAULT_NODE_VERSION

# -----------------------------------------------------------
# PERMISSIONS
chown 33:33 /var/www/.nvm -R

# -----------------------------------------------------------------------------------------
# PREPARE BASHRC
echo "source /var/www/.nvm/nvm.sh" >> /var/www/.bashrc
chown 33:33 /var/www/.bashrc
echo "export BASH_ENV=${BASH_ENV}" >> /etc/profile


