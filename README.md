finance
=======

`finance` is a financial tracking and budgeting web app powered by [Django](https://www.djangoproject.com/) and Python 3.

The app works by parsing bank statements that have been [exported from online banking](#supported-statements) and importing them into a relational database. It recognises counterparties based on regex patterns you setup, and automatically categorises these transactions for effortless budgeting and easy-to-read spending metrics.

Features
--------

### Currently available

- Importing bank statements from Santander
- Automatic categorisation of transactions based on counterparty (matched from regex patterns)

### Planned

- Categorical budgeting (weekly/monthly)
- Spending metrics (e.g., monthly cash in/out)

### Limitations

- Only supports a single user with a single bank account
- Only one bank supported

Installation
------------

### Prerequisites
- [Python 3.4](https://www.python.org/downloads/)
- [node.js](http://nodejs.org/)

### Step-by-step
1. Clone the code repository and `cd` into it
2. Run the `install.bat` or `install.sh` script to download Node and Python dependencies. This will setup a virtual environment under `env/`, and then run `manage.py update` to compile front-end assets and setup the database.
3. Done!

Supported statements
--------------------

To import bank statements into the system, run:
```
Windows> manage.bat importstatement <importer name> <path to file>
$ ./manage.sh importstatement <importer name> <path to file>
```

Bank | Format | Importer name
---- | ------ | -------------
Santander UK | .txt | `santander.text`
