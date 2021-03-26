# staff_data_engineer_assessment

The following questions will be used to assess your ability to design, architect maintainable and scalable code.   Please fork this repo.

Submit everything needed to execute and validate your solutions for each of your answers.

Writing comprehensive tests are critical when submitting your solution.

1. **SQL**

Write a stored procedure that accepts the following parameters:  first name, last name, date of birth, email and gender.  First, Last, email and one additional parameter are required to execute a match.  Return the id, decision( exact, possible, no match or unable to match) and score.   Be mindful of performance.
* Note:  You must create your own Database and tables for this.  Please provide all scripts so that the evaluator can execute and validate your solutions. 
2. **Python**

Leveraging python (no direct SQL please) import the two csv files in the repo.
* a. Create a staged version of the data
* b. Create a clinician mart
* c. Only store clinical titles
* d.Store only number after the "-"
* e. Create - Unique NPIs only
* f.Write tests


# WORKING WITH THIS PROJECT

## Using `make`

This project takes advantage of `make` to make interacting with building and testing easier for the developer.  Use the following make commands from the project's root to do interesting things.

* `make build` - re-builds and starts the docker containers
* `make start` - starts up the postgres and python containers in detached mode
* `make stop` - spins down the docker containers using docker-compose down
* `make db_connect` - launches an interactive console directly connected to postgres
* `make db_bash` - launches an interactive session with the postgres docker container at /bin/bash
* `make db_test` - executes the test_person_match.sql on the postgres database.
* `make py_bash` - launches an interactive session with the python3.8 docker.
* `make py_test` - launches the unit tests using pytests and integration/file based tests using exec
* `make full_test` - launches `db_test` then `py_test` so tests can be done in a single command.
 
## Using your IDE
If desired, after `make build` or `make start` the PostgeSQL database will be running on port 5432 on localhost.  You can connect to it from any IDE of your
choosing to interact with the database:
    `postgresql://localhost:5432/postgres`

## Testing
To test, you need to only build the containers using `make build` and then choose the tests to run, either `make db_test` or `make py_test`


