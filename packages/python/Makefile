init:
	pip install -r requirements.txt

test:
	nosetests tests

build_assets:
	cd ../.. && pnpm install && cd packages/javascript/visualizer && pnpm build

build_package:
	python3 -m build


build_diagraph:
	make build_assets
	make build_package
