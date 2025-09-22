# Changes in Project

All notable changes of releases are documented in this file
using the [Keep a CHANGELOG](https://keepachangelog.com/) principles.

This changelog primarily focuses on changes to the **dockware/shopware-essentials** image.
Because this is the foundation of the Shopware environment, we will always release a new essentials version if something
changes in the operating system or packages. New Shopware versions, built with this version, will then automatically
contain these changes.

## [Unreleased]

### Added

- Add conditional NVM decompression to prevent restart failures (thx @susannekoerber)

### Changed

- Replace recursive chown with selective find commands for Git-safe permissions (thx @susannekoerber)
- Preserves Git repository permissions when mounting directories with .git folders (thx @susannekoerber)

### Fixed

- Fixes container restart loop when NVM archive is missing after first run (thx @susannekoerber)

## [1.0.0]

- Initial release (Ubuntu 24.04, PHP 8.2/8.3/8.4, Node 22/24)