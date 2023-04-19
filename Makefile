.PHONY : lint runserver test makemessages compilemessages

lint:
	flake8 .

format:
	black .

sort:
	isort .

start:
	python manage.py runserver

test:
	python manage.py test

tf_fmt:
	terraform fmt -recursive ./.tf

tf_init:
	terraform -chdir=".tf/composition/api/eu-central-1/$(env)/" init

tf_validate:
	terraform -chdir=./.tf/composition/api/eu-central-1/$(env)/ validate

tf_plan:
	terraform -chdir=./.tf/composition/api/eu-central-1/$(env)/ plan

tf_apply:
	terraform -chdir=./.tf/composition/api/eu-central-1/$(env)/ apply --auto-approve

stripe_login:
	stripe login

stripe_listen:
	stripe listen --forward-to localhost:8000/stripe/webhook/

stripe_trigger:
	stripe trigger $(event)
