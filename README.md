# Dockware for Shopware

[![MIT licensed](https://img.shields.io/github/license/dockware/shopware.svg?style=flat-square)](https://github.com/dockware/dockware/blob/master/LICENSE)
![Docker Pulls](https://img.shields.io/docker/pulls/dockware/shopware)
![Docker Image Size](https://img.shields.io/docker/image-size/dockware/shopware)

Welcome to Dockware! For more information, visit [dockware.io](https://dockware.io).

<!-- TOC -->

* [Dockware for Shopware](#dockware-for-shopware)
    * [What is Dockware for Shopware?](#what-is-dockware-for-shopware)
    * [When to use this image?](#when-to-use-this-image)
    * [Versioning](#versioning)
        * [Docker Tags](#docker-tags)
        * [Git Tags](#git-tags)
        * [Essentials-First](#essentials-first)
        * [LTS](#lts)
        * [Patches](#patches)
    * [Deprecations and Legacy services](#deprecations-and-legacy-services)
    * [Quick Start](#quick-start)
        * [Docker Run](#docker-run)
        * [Docker Compose](#docker-compose)
        * [Watchers](#watchers)
    * [Documentation](#documentation)
    * [Shopware Guidelines](#shopware-guidelines)
    * [Contribution](#contribution)
    * [License](#license)

<!-- TOC -->

## What is Dockware for Shopware?

Our Dockware images are optimized Docker images for web development in general, but also for Symfony and Shopware projects.

This repository contains the source code for 2 images **dockware/shopware** and **dockware/shopware-essentials**.
It's a perfect match if you work with Shopware 6.

While the **shopware-essentials** image comes with everything you need to run your own Shopware version inside a single container,
the pure **shopware** image comes with an installed and prepared Shopware 6 instance, so you can immediately start developing.

All required services such as MySQL, but also additional things like AdminerEVO, PimpMyLog, etc. are included in both images.
Developers benefit from ready to use features like Xdebug, switching of PHP versions, Node versions and more.

## When to use this image?

These images are a perfect fit for the following use cases.

* Explore any Shopware 6 version
* Develop Shopware 6 plugins, apps, themes
* Use it in pipelines if you need an easy Shopware 6 instance for testing or more

If you develop full Shopware 6 shops, we recommend either using the **shopware-essentials** image, or even the **dockware/web** image, if you
know how to use Docker and want to fully rebuild your production environment locally.

## Versioning

While we generally use semantic versioning for other images, the **dockware/shopware** is a bit different.
We try to use 1 image (name), and therefore we have to use the Docker tag to indicate the **Shopware version**.

This also gives you the experience, that you can just write any supported Shopware 6 version as tag, without thinking,
and you end up with the correct image and correct Shopware 6 version.

The **dockware/shopware-essentials** image is versioned with semantic versioning
and will always be updated if relevant changes are made in the operating system or packages.
Shopware versions that are then built afterward will automatically contain these changes.

The source code in this repository is always the **latest Shopware version**.

### Docker Tags

The **dockware/shopware** image is published on Docker Hub with the following tags:

* `latest` — points to the most recent Shopware version overall
* `<major>-latest` — points to the most recent version of a Shopware major release, e.g. `6.7-latest` or `6.6-latest`
* `<version>` — a specific Shopware version, e.g. `6.7.10.0`

The `<major>-latest` tags are useful if you want to stay on a specific Shopware major (e.g. for an LTS branch) without manually updating to every new patch release.

```bash
# always the latest released Shopware version
docker run -p 80:80 dockware/shopware:latest

# always the latest patch of Shopware 6.7
docker run -p 80:80 dockware/shopware:6.7-latest

# pinned to a specific Shopware version
docker run -p 80:80 dockware/shopware:6.7.10.0
```

### Git Tags

We use Git Tags to indicate releases.

**Shopware versions** will get tags based on the Shopware version and this pattern: `sw-6.7.2.1`.

If an older Shopware version needs a fix, we will create a separate branch for this where we fix the issue and create a second tag like `sw-6.6.0.0-v2`.

The **shopware-essentials** image will get tags like `essentials-1.0.0` and more.

Please keep in mind, that we try to avoid rebuilding existing Shopware versions.
Therefore, the used essentials version (operating system stuff) is the one that was available at the time of the build.

### Essentials-First

As seen in the changelog.md, we focus primarily on the **shopware-essentials** image.
So every change of the image and its features should lead to a new changelog entry.

The bundled Shopware installation is only the small addon to the actual essentials image.

Therefore, when releasing a new Shopware version, we will ensure to first release the official new version of the essentials image,
if any changes where made to it, and then release the Shopware version on top of it.

### LTS

The source code of this repository is always the latest Shopware version.
Shopware still releases minor releases for older major versions (LTS) and therefore we sometimes need to create new images for these versions.

This is done by adding new branches like **lts/sw-X.Y.z** based on the latest main branch if possible.
In this branch, additional adjustments are done for the old version, like adjusting PHP and Node versions and maybe more.

After finishing the changes, a new tag like `sw-X.Y.z` is created in this branch and a new Docker Image is released.

### Patches

We do not update existing Shopware Docker images once they are released.
In case we find a critical issue that needs to be fixed, we will create a new version like **X.Y.z-v2**.

These fixes will be done in a separate branch with the **base version name** of the Shopware version like **lts/sw-X.Y.z**.
The branch will be based on the original release tag of the Shopware version.

The first **and all upcoming patches** of this version will be done in this branch with additional tags being added to GIT.

## Deprecations and Legacy services

One thing that is important to us, is that we try to keep the image as slim as possible for developers.
Therefore we only include packages like PHP, Node, etc. in versions, that are supported by the Shopware version of the image.

Please keep in mind, that this is the **next generation** of our dockware images.
You may find older Shopware versions in the images **dockware/dev** or **dockware/play**.

## Quick Start

### Docker Run

This is how you launch a Shopware 6 version with Port 80 (HTTP).
Your shop is then available at http://localhost.

You can see when the container is ready by checking the logs with **docker logs**
It usually just needs a few seconds after downloading the image.

```bash 
# launch a Shopware available at http::/localhost
docker run -p 80:80 dockware/shopware:6.7.2.0
```

### Docker Compose

This is the same as the docker run command, but as docker-compose.yml file.
In addition, it has **optional environment** variables for PHP and Node versions.

> Please keep in mind, your image will crash if you use PHP or Node versions that do not exist in the image tag version.

```yaml
  shop:
    image: dockware/shopware:6.7.2.0
    ports:
      - 80:80
    environment:
      - PHP_VERSION=8.4
      - NODE_VERSION=20
```

### Watchers

You can easily start the watchers for Shopware by using our predefined **makefile commands**.
First make sure to expose the required ports 5173 for Admin and 9999/9998 for Storefront.
You can do all 3 of them, or just expose what you need.

```bash
docker run -p 80:80 -p 5173:5173 -p 9999:9999 -p 9998:9998 dockware/shopware:6.7.2.0
```

Then connect into your container and open the makefile in **/var/www**.
Type in "make" and press ENTER to see all available commands.

```bash
# starts admin watcher
make watch-admin
# starts storefront watcher
make watch-storefront
```

## Documentation

For all these cool features like Xdebug, Filebeat, PHP Switching, Supervisor and more,
please check out the Docs at [https://dockware.io](https://dockware.io).

## Shopware Guidelines

We follow the Shopware guidelines for system requirements and release policies.

* System Requirements: https://docs.shopware.com/en/shopware-6-en/first-steps/system-requirements
* Release Policty: https://developer.shopware.com/release-notes/

## Contribution

Contributions are welcome! Please refer to the `CONTRIBUTING.md` file for guidelines on how to contribute effectively.

## License

Dockware for Shopware is provided under the MIT license. As with all Docker images, this project may include software under other licenses.
Users are responsible for ensuring compliance with all relevant licenses for software contained within the image.