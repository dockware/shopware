# Changes in Project

All notable changes of releases are documented in this file
using the [Keep a CHANGELOG](https://keepachangelog.com/) principles.

This changelog primarily focuses on changes to the **dockware/shopware-essentials** image.
Because this is the foundation of the Shopware environment, we will always release a new essentials version if something
changes in the operating system or packages. New Shopware versions, built with this version, will then automatically
contain these changes.

## [Unreleased]

### Added

- Added a built-in healthcheck. You can now use "docker compose up --wait" to wait until the container is fully ready. (@thx for that brilliant idea @BlackScorp)

### Fixed

- Mailcatcher was not correctly configured to be used in SSMTP configurations.
- Remove a default PHP switch to v8.3 before installing Shopware. We just stick to the default version from the PHP installation part.

## [1.2.0]

### Changed

- Remove "Xdebug Beta" for PHP 8.4 and switch to official release

### Fixed

- It was possible to start the image with an unsupported Node version which led to problems. The container will now crash during startup to give you immediate feedback.

## [1.1.0]

### Added

- Add conditional NVM decompression to prevent restart failures (thx @susannekoerber)
- Add "patch" package to support Composer Patching vendors.

### Changed

- Replace recursive chown with selective find commands for Git-safe permissions (thx @susannekoerber)
- Preserves Git repository permissions when mounting directories with .git folders (thx @susannekoerber)

### Fixed

- Fixes container restart loop when NVM archive is missing after first run (thx @susannekoerber)

## [1.0.0]

- Initial release (Ubuntu 24.04, PHP 8.2/8.3/8.4, Node 22/24)