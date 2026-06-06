.PHONY: help build
.DEFAULT_GOAL := help


# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------
# adjust the shopware version here!
# this is the one, that will be installed in the shopware image
# however, it the tag can still use "dev-main" as version for nightly builds while still this version is installed
CURRENT_SW_VERSION:=6.7.10.2
# ------------------------------
# this is the minimum php version for Shopware, it will be installed using this version
CURRENT_SW_VERSION_MIN_PHP:=8.2

# ----------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------

help:
	@echo "PROJECT COMMANDS"
	@echo "--------------------------------------------------------------------------------------------"
	@printf "\033[33mInstallation:%-30s\033[0m %s\n"
	@grep -E '^[a-zA-Z_-]+:.*?##1 .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?##1 "}; {printf "\033[33m  - %-30s\033[0m %s\n", $$1, $$2}'
	@echo "--------------------------------------------------------------------------------------------"
	@printf "\033[36mDevelopment:%-30s\033[0m %s\n"
	@grep -E '^[a-zA-Z_-]+:.*?##2 .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?##2 "}; {printf "\033[36m  - %-30s\033[0m %s\n", $$1, $$2}'
	@echo "--------------------------------------------------------------------------------------------"
	@printf "\033[35mDevOps:%-30s\033[0m %s\n"
	@grep -E '^[a-zA-Z_-]+:.*?##3 .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?##3 "}; {printf "\033[35m  - %-30s\033[0m %s\n", $$1, $$2}'
	@echo "--------------------------------------------------------------------------------------------"
	@printf "\033[32mTests:%-30s\033[0m %s\n"
	@grep -E '^[a-zA-Z_-]+:.*?##4 .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?##4 "}; {printf "\033[32m  - %-30s\033[0m %s\n", $$1, $$2}'

# ----------------------------------------------------------------------------------------------------------------

install: ##1 Installs all dependencies
	composer install
	cd tests/cypress && make clean
	cd tests/cypress && make install

clean: ##1 Clears all dependencies dangling images
	rm -rf vendor/*
	rm -rf node_modules/*
	cd tests/cypress && make clean
	docker images -aq -f 'dangling=true' | xargs docker rmi
	docker volume ls -q -f 'dangling=true' | xargs docker volume rm

# ----------------------------------------------------------------------------------------------------------------

dev-essentials: ##2 Dev-Helper that builds, tests and analyzes the image
	@echo "Building: dockware/shopware-essentials:dev-main"
	make build-essentials version=dev-main
	make svrunit image=shopware-essentials tag=dev-main
	make analyze image=shopware-essentials tag=dev-main

dev-shopware: ##2 Dev-Helper that builds, tests and analyzes the image
	@echo "Building: dockware/shopware:dev-main"
	make build-shopware tag=dev-main
	make svrunit image=shopware tag=dev-main
	make cypress tag=dev-main
	make analyze image=shopware tag=dev-main

# ----------------------------------------------------------------------------------------------------------------

build-essentials: ##3 Builds the Essentials image [version=x.y.z|dev-main]
ifndef version
	$(error Please provide the argument version=xyz to run the command)
endif
	@cd ./src && DOCKER_BUILDKIT=1 docker build --squash --no-cache --build-arg VERSION=none -t dockware/shopware-essentials:$(version) .

build-shopware: ##3 Builds with the current Shopware version [tag=x.y.z|dev-main]
ifndef tag
	$(error Please provide the argument tag=xyz to run the command)
endif
	@cd ./src && DOCKER_BUILDKIT=1 docker build --squash --no-cache --build-arg VERSION=$(CURRENT_SW_VERSION) --build-arg MIN_PHP=$(CURRENT_SW_VERSION_MIN_PHP) -t dockware/shopware:$(tag) .

analyze: ##3 Shows the size of the image [image=shopware|shopware-essentials, tag=x.y.z|dev-main]
ifndef image
	$(error Please provide the argument image=xyz to run the command)
endif
ifndef tag
	$(error Please provide the argument tag=xyz to run the command)
endif
	docker history --format "{{.CreatedBy}}\t\t{{.Size}}" dockware/$(image):$(tag) | grep -v "0B"
	# --------------------------------------------------
	docker save -o dev.tar dockware/$(image):$(tag)
	gzip dev.tar
	ls -lh dev.tar.gz
	# --------------------------------------------------
	rm -rf dev.tar
	rm -rf dev.tar.gz | true

# ----------------------------------------------------------------------------------------------------------------

svrunit: ##4 Runs all SVRUnit tests against an image [image=shopware|shopware-essentials, tag=x.y.z|dev-main]
ifndef image
	$(error Please provide the argument image=xyz to run the command)
endif
ifndef tag
	$(error Please provide the argument tag=xyz to run the command)
endif
	php ./vendor/bin/svrunit test --configuration=./tests/svrunit/suites/$(image).xml --docker-tag=$(tag) --debug --report-junit --report-html


cypress: ##4 Runs all Cypress tests for the Shopware image [tag=x.y.z|dev-main]
ifndef tag
	$(error Please provide the argument tag=xyz to run the command)
endif
	cd ./tests/cypress && make install;
	cd ./tests/cypress && make start-env image=shopware tag=$(tag);
	# -------------------------------------------------------------------------
ifeq ($(tag),dev-main)
	@# if we have dev-main as tag, then always use the CURRENT_SW_VERSION for testing
	cd ./tests/cypress && make run url=http://localhost:1000 shopware=$(CURRENT_SW_VERSION) || (make stop-env && false)
else
	cd ./tests/cypress && make run url=http://localhost:1000 shopware=$(tag) || (make stop-env && false)
endif
