# BDLawsViz

## Create virtualenv bucketlistenv

	$ virtualenv lawenv
	$ source ./lawenv/bin/activate


## Setting up environment

### Create Virtual Environment

    $ virtualenv -p python3 lawenv


### Install packages

    $ pip install flask
    $ pip install flask-mysql
    $ pip install pymongo
    $ pip install nltk
	$ pip install flask-login

#### Installing spaCy

    $ pip install spacy
    $ python -m spacy download en
( first download the en_core_web_sm-1.2.0.tar.gz package from https://github.com/explosion/spacy-models )
    $ pip install en_core_web_sm-1.2.0.tar.gz



### Installing everything automatically

    $ pip install -r requirements.txt

## Running in Linux console:

	$ source scripts/build.sh


## Notes:

    - If javascript files seem persistent and changes not showing in browser,
        then force re-load browser: ctrl + F5

    - Used MySQL stored procedures

    - Used spaCy

-used MongoDB for performing searches


## MongoDB

- Instantiating Mongo Server

mongod --dbpath /path/to/mongodb --port mongo_port

or

source scripts/build.sh


- Import bson using mongorestore:

mongorestore --port mongo_port db_name -c collection_name path/file.bson

eg.

mongorestore --port 4000 -d law -c bigrams `pwd`/bigrams.bson
mongorestore --port 4000 -d law -c trigrams `pwd`/trigrams.bson
mongorestore --port 4000 -d law -c laws `pwd`/laws.bson


## MySQL

    Login through terminal:

        $ mysql -u <username> -p

### Adding MySQL Stored Procedures

    Get All Names:
        DELIMITER $$
        USE `KolpoKoushol`$$
        DROP PROCEDURE IF EXISTS `sp_getAllNames` $$
        CREATE PROCEDURE `sp_getAllNames` ()
        BEGIN
            select * from lawIDs;
        END$$
        DELIMITER ;

    Get All Edges:
        DELIMITER $$
        USE `KolpoKoushol`$$
        DROP PROCEDURE IF EXISTS `sp_getAllEdges` $$
        CREATE PROCEDURE `sp_getAllEdges` ()
        BEGIN
            select * from bdlaws_edges;
        END$$
        DELIMITER ;

    Searching law name using id:
        DELIMITER $$
        USE `KolpoKoushol`$$
        DROP PROCEDURE IF EXISTS `sp_searchName` $$
        CREATE PROCEDURE `sp_searchName` (
        IN law_id bigint
        )
        BEGIN
            select L1.name as qname from lawIDs as L1 where L1.id = law_id;
        END$$
        DELIMITER ;

    Searching outdegree ids using searched id:
        DELIMITER $$
        USE `KolpoKoushol`$$
        DROP PROCEDURE IF EXISTS `sp_searchOutDegree` $$
        CREATE PROCEDURE `sp_searchOutDegree` (
        IN law_id bigint
        )
        BEGIN
            select E.source as idS, L1.name as nameS, E.destination as idD, L2.name as nameD from bdlaws_edges as E LEFT OUTER JOIN lawIDs as L1 ON E.source = L1.id LEFT OUTER JOIN lawIDs as L2 ON E.destination = L2.id where E.source = law_id;
        END$$
        DELIMITER ;

    Searching indegree ids using searched id:
        DELIMITER $$
        USE `KolpoKoushol`$$
        DROP PROCEDURE IF EXISTS `sp_searchInDegree` $$
        CREATE PROCEDURE `sp_searchInDegree` (
        IN law_id bigint
        )
        BEGIN
            select E.source as idS, L1.name as nameS, E.destination as idD, L2.name as nameD from bdlaws_edges as E LEFT OUTER JOIN lawIDs as L1 ON E.source = L1.id LEFT OUTER JOIN lawIDs as L2 ON E.destination = L2.id where E.destination = law_id;
        END$$
        DELIMITER ;

    Creating User Table:
        CREATE TABLE `KolpoKoushol`.`tbl_user` (
          `user_id` BIGINT AUTO_INCREMENT,
          `user_name` VARCHAR(45) NULL,
          `user_username` VARCHAR(45) NULL,
          `user_password` VARCHAR(45) NULL,
          PRIMARY KEY (`user_id`));

    Creating a user:
        DELIMITER $$
        USE `KolpoKoushol`$$
        DROP PROCEDURE IF EXISTS `sp_createUser` $$
        CREATE PROCEDURE `sp_createUser` (
            IN p_name VARCHAR(20),
            IN p_username VARCHAR(20),
            IN p_password VARCHAR(20)
        )
        BEGIN
            if ( select exists (select 1 from tbl_user where user_username = p_username) ) THEN
                select 'Username Exists !!';
            ELSE
                insert into tbl_user
                (
                    user_name,
                    user_username,
                    user_password
                )
                values
                (
                    p_name,
                    p_username,
                    p_password
                );
            END IF;
        END$$

    Validating login:
        DELIMITER $$
        USE `KolpoKoushol`$$
        DROP PROCEDURE IF EXISTS `sp_validateLogin` $$
        CREATE PROCEDURE `sp_validateLogin` (
            IN p_username VARCHAR(20)
        )
        BEGIN
            select * from tbl_user where user_username = p_username;
        END$$
        DELIMITER ;

## Trivial

###
