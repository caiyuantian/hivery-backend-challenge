# Prerequisite: Installation packages and setup database
1. What I installed is python 3.7.4, Flask 1.1.1, it should be work by using python >= 3 and Flask >= 1.0.

2. Install dependency package
    1) Ubuntu: Install libmysqlclient-dev
        sudo apt-get install libmysqlclient-dev
    2) If you cannot install mysqlclient by pip3 in Windows, do it manually by install following whl package 
        mysqlclient-1.4.2-cp37-cp37m-win32.whl

3. Install modules
    pip3 install flask flask_mysqldb flask-httpauth

4. If you are using mysql version > 8.0.4, you need to change the authentication method by adding following option to config file and then re-inititialize mysql
    [mysqld]
    default_authentication_plugin=mysql_native_password

5. Create a new mysql user hivery and grant privileges by following commands
    CREATE USER 'hivery'@'localhost' IDENTIFIED BY 'Hivery123@';
    grant all privileges on *.* to 'hivery'@'localhost';
    quit

    NOTE: If you are using different mysql user and database, please make sure following config the config.py file under project folder is updated accordingly.
        MYSQL_USER = 'hivery'
        MYSQL_PASSWORD = 'Hivery123@'
        MYSQL_DB = 'hivery'

6. Login mysql by new user hivery
    mysql -u hivery -p

7. Create database
	CREATE DATABASE hivery;

8. Create tables

    use hivery;

    CREATE TABLE IF NOT EXISTS `companies`(
        `guid` CHAR(36) UNIQUE NOT NULL,
        `index` INT UNIQUE NOT NULL,
        `company` VARCHAR(50),
        PRIMARY KEY NONCLUSTERED ( `guid` ),
        INDEX CIX_COMPANIES (`index`)
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;

    CREATE TABLE IF NOT EXISTS `people`(
        `guid` CHAR(36) UNIQUE NOT NULL,
        `index` INT NOT NULL,
        `has_died` TINYINT(1),
        `balance` FLOAT,
        `picture` VARCHAR(50),
        `age` INT UNSIGNED,
        `eyeColor` CHAR(10),
        `name` VARCHAR(50),
        `gender` CHAR(6),
        `company_id` INT,
        `email` VARCHAR(50),
        `phone` VARCHAR(20),
        `address` VARCHAR(100),
        `about` VARCHAR(1000),
        `registered` DATETIME,
        PRIMARY KEY NONCLUSTERED ( `guid` ),
        INDEX CIX_PEOPLE (`index`)
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;

    CREATE TABLE IF NOT EXISTS `friends`(
        `_id` INT UNSIGNED AUTO_INCREMENT,
        `index` INT NOT NULL,
        `friend_index` INT NOT NULL,
        PRIMARY KEY ( `_id` ),
        INDEX CIX_FRIENDS (`index`)
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;

    CREATE TABLE IF NOT EXISTS `foods`(
        `_id` INT UNSIGNED AUTO_INCREMENT,
        `index` INT NOT NULL,
        `food_type` TINYINT,
        `favouriteFood` VARCHAR(20),
        PRIMARY KEY ( `_id` ),
        INDEX CIX_FOODS (`index`)
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;

## How to run this application?
1. Clone this project from github
    git clone https://github.com/caiyuantian/hivery-backend-challenge.git

2. Go into the folder and run
    cd hivery-backend-challenge
    python app.py

## How to do test?
1. A simple default page is created as below
    http://localhost:5000/

    You can upload the new companies.json and people.json files to refresh the database in follow URL
    http://localhost:5000/upload

    there is authenticate before use the API, default user name and password are both 'admin', you can change them in function check_auth of file auth.py

## test cases:
1. normal case for company
	http://localhost:5000/api/v1/company/1/employees
2. abnormal case for company with zero people
	http://localhost:5000/api/v1/company/0/employees
3. normal case for 2 people with 1 common friend
	http://localhost:5000/api/v1/people/3,4
4. normal case for 2 people with 2 common friends
	http://localhost:5000/api/v1/people/5,6
5. abnormal case for 2 people with no common friend
	http://localhost:5000/api/v1/people/1,2
6. error case for input more than 2 people
	http://localhost:5000/api/v1/people/2,3,4
7. normal case for 1 people
	http://localhost:5000/api/v1/people/2
8. abnormal case for 1 people
	http://localhost:5000/api/v1/people/2,
9. abnormal case for 1 people
	http://localhost:5000/api/v1/people/2%
10. abnormal case for 1 people
	http://localhost:5000/api/v1/people/2*
11. abnormal case for 1 people
	http://localhost:5000/api/v1/people/*
12. abnormal case for 1 people
	http://localhost:5000/api/v1/people/222222222222222222222222222222222
13. abnormal case for 2 people
	http://localhost:5000/api/v1/people/2,3,
14. abnormal case for 2 people
	http://localhost:5000/api/v1/people/2,3%
15. abnormal case for 2 people
	http://localhost:5000/api/v1/people/2,3*
16. unusual case for 2 people
	http://localhost:5000/api/v1/people/2,333333333333333333333333333333333333
17. unusual case for 2 people
	http://localhost:5000/api/v1/people/22222222222222222222222222222222222,3
18. unusual case for 2 people
	http://localhost:5000/api/v1/people/22222222222222222222222222222222222,33333333333333333333333333333333333

# future work
1. API traffic control, i.e. limit a user to use specific times in a period, and add blacklist function.
2. Extend Authentication function to support multiple users. Can be easily done by adding a user table.
3. More API functions