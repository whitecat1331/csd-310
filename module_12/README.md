Install Steps:

First clone the repository:
git clone https://github.com/whitecat1331/csd-310.git

Next, install the dependencies:
pip install -r requirements.txt

SQL Connection Steps:

Start MySQL, then source the whatabook_init.sql file to initilize the user and database.

-- Linux --
sudo service mysql start

sudo systemctl start mysql 

-- Windows CLI --
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld"

Configuration:
The configuration file should be included within the repository and modeul_12 named config.ini (Note: depracated commits have it named .config)

Environment Variables:
The environment variables SQL_USER and PASSWORD must be set for the program to run.

Environment variables can be created locally using the CLI or by creating an environment file in module_12 named .env

-- Linux --
export SQL_USER=whatabook_user
export PASSWORD=MySQL8IsGreat!

-- Windows CLI --
set SQL_USER=whatabook_user
set PASSWORD=MySQL8IsGreat!

or 

-- Recommended to use .env file --
SQL_USER=whatabook_user
PASSWORD=MySQL8IsGreat!


Start Program:
python whatabook.py


Trubleshooting/Debugging:
If you run into any issues, first make sure the files config.ini and .env are set and are not empty.

Next, there are unit test provided for the Whatabook and Whatabookmenu classes. You can try to run these unit tests to help with any further issues.

Debug Command:
python -m unittest -v test_whatabook.py
or 
pyhton -m unittest -v test_whatabookmenu.py

Developer Notes:
Due to time constraints, documentation and testing for this program is not as thorough.
Comments and more error handling will be added throughout so make sure to pull often using "git pull"
For classmates, if there are any further issues setting the project up or with the project itself, let me know in the discussion.


