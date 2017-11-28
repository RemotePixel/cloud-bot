
SHELL = /bin/bash

all: build package

build:
	docker build --tag lambda:latest .

package:
	docker run \
		-w /var/task/ \
		--name lambda \
		-itd \
		lambda:latest
	docker cp lambda:/tmp/package.zip package.zip
	docker stop lambda
	docker rm lambda


shell:
	docker run \
		--name lambda  \
		--volume $(shell pwd)/:/data \
		--rm \
		-it \
		lambda:latest /bin/bash

clean:
	docker stop lambda
	docker rm lambda
