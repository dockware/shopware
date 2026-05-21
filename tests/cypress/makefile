.PHONY: help
.DEFAULT_GOAL := help


help:
	@echo "PROJECT COMMANDS"
	@echo "--------------------------------------------------------------------------------------------"
	@printf "\033[33mInstallation:%-30s\033[0m %s\n"
	@grep -E '^[a-zA-Z_-]+:.*?##1 .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?##1 "}; {printf "\033[33m  - %-30s\033[0m %s\n", $$1, $$2}'
	@echo "--------------------------------------------------------------------------------------------"
	@printf "\033[36mEnvironment:%-30s\033[0m %s\n"
	@grep -E '^[a-zA-Z_-]+:.*?##2 .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?##2 "}; {printf "\033[36m  - %-30s\033[0m %s\n", $$1, $$2}'
	@echo "--------------------------------------------------------------------------------------------"
	@printf "\033[32mTests:%-30s\033[0m %s\n"
	@grep -E '^[a-zA-Z_-]+:.*?##3 .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?##3 "}; {printf "\033[32m  - %-30s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------------------------

install: ##1 Installs all dependencies
	npm install

clean: ##1 Cleans all dependencies
	rm -rf node_modules

# ---------------------------------------------------------------------------------------------


start-env: ##2 Starts the environment
ifndef image
	$(error Please provide the argument image=xyz to run the command)
endif
ifndef tag
	$(error Please provide the argument tag=xyz to run the command)
endif
	docker rm -f shopware_cypress || true
	docker run --rm -p 1000:80 --name shopware_cypress -d dockware/$(image):$(tag)
	until [ "$$(docker inspect -f '{{.State.Health.Status}}' shopware_cypress)" = "healthy" ]; do sleep 1; done
	docker exec shopware_cypress bash -c "mysql -h 127.0.0.1 -u root -proot shopware -e \"UPDATE sales_channel_domain SET url = CONCAT(url, ':1000') WHERE url LIKE 'http://localhost%';\""

stop-env: ##2 Stops the environment
	docker rm -f shopware_cypress || true

# ---------------------------------------------------------------------------------------------

open-ui: ##3 Opens Cypress UI (make open-ui url=xy shopware=xy)
ifndef url
	$(warning Please provide the URL argument to Start Cypress!)
	@exit 1
endif
ifndef shopware
	$(warning Please provide the shopware version argument to Start Cypress!)
	@exit 1
endif
	CYPRESS_BASE_URL=$(url) CYPRESS_SHOPWARE=$(shopware) ./node_modules/.bin/cypress open --env conf=dev

run: ##3 Runs all E2E tests for Flex (make run url=xy shopware=xy)
ifndef url
	$(warning Please provide the URL argument to Start Cypress!)
	@exit 1
endif
ifndef shopware
	$(warning Please provide the shopware version argument to Start Cypress!)
	@exit 1
endif
	CYPRESS_BASE_URL=$(url) CYPRESS_SHOPWARE=$(shopware) ./node_modules/.bin/cypress run --headless
