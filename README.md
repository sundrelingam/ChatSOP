# Setup

1. Create and enter the virtual environment with:

* `python3 -m venv venv`
* `source ./venv/bin/activate`
* `python3 -m pip install -r requirements.txt`

2. Add your OpenAI API key to `settings.py`.

3. Make Django migrations (sets up database). This needs to be done from the `chatsop` subfolder.

* `python3 manage.py makemigrations`
* `python3 manage.py migrate`
* `python3 manage.py makemigrations uploads_app`
* `python3 manage.py migrate uploads_app`
* `python3 manage.py makemigrations payments_app`
* `python3 manage.py migrate payments_app`

4. Run the application:

* `python3 manage.py runserver`