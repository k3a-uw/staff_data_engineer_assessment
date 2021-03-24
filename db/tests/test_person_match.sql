CREATE OR REPLACE FUNCTION test_person_match()
RETURNS TABLE (
  test_name VARCHAR,
  test_results VARCHAR
)

LANGUAGE plpgsql
AS $$
BEGIN
-- INSERT SOME TEST DATA INTO THE EMPTY HUMANS TABLE SO WE CAN GUARANTEE EXPECTED RESULTS
DELETE FROM HUMANS;
INSERT INTO HUMANS
  (id, given_name, family_name, email_address, date_of_birth, gender)
VALUES
   (1, 'Person 1', 'Family 1', 'test@test.com', '2000-01-01', 'M')
, (2, 'Person 2', 'Family 1', 'test2@test.com', '2000-01-02', 'F')
, (3, 'Person 3', 'Family 1', 'test3@test.com', '2000-12-31', 'X')
, (4, 'Person 4', 'Family 2', 'test4@test.com', '2001-12-30', 'M')
, (5, 'Steve', 'O''neil', 'test5@test.com', '2010-01-01', NULL)
, (6, 'Mary',  'Smith', 'test6@test.com', NULL, NULL)
, (7, 'Another', 'Name', 'test7@test.com','2020-01-01', NULL)
, (8, 'Person 1', 'Family 1', 'test8@test.com', '2000-01-02', 'F')
;

-- CREATE THE TEST CASES AS A DATABASE TABLE FOR FAST EXECUTION
-- USING CROSS (LATERAL) JOIN AND ASSERT RESULTS
-- THESE TESTS COULD BE STORED IN A CSV FILE AND LOADED IF DESIRED
DROP TABLE IF EXISTS test_temp;
CREATE TEMPORARY TABLE test_temp (
    test_name VARCHAR(128)
  , arg1      VARCHAR(128)
  , arg2      VARCHAR(128)
  , arg3      DATE
  , arg4      VARCHAR(128)
  , arg5      CHAR(1)
  , assert1   INT
  , assert2   VARCHAR(128)
  , assert3   FLOAT
);

INSERT INTO test_temp
  (test_name, arg1, arg2, arg3, arg4, arg5, assert1, assert2, assert3)
VALUES
  ('Exact Match ID:1', 'Person 1', 'Family 1', '2000-01-01', 'test@test.com','M', 1, 'Exact Match', 1)
, ('Partial Match (gender) ID:1', 'Person 1', 'Family 1', '2000-01-02', 'test@test.com','M', 1, 'Partial Match', 0.25)
, ('Partial Match (dob) ID:1', 'Person 1', 'Family 1', '2000-01-01', 'test@test.com','F', 1, 'Partial Match', 0.75)
, ('Exact Match ID:8', 'Person 1', 'Family 1', '2000-01-02', 'test8@test.com', 'F', 8, 'Exact Match', 1)
, ('No Match (no matching fields)', 'NotIntheSystem','NotIntheSystem','1970-01-01','NotIntheSystem', 'P', -1, 'No Match found', 0)
, ('No Match (First Last Only)', 'Person 1', 'Family 1', '1970-01-01', 'NotIntheSystem', 'P', -1, 'No Match found', 0)
, ('No Match (First Last Email Only)', 'Person 4', 'Family 2', '1970-01-01', 'NotIntheSystem', 'P', -1, 'No Match found', 0)
, ('No Match (First Last DOB Only)', 'Person 4', 'Family 2', '2001-12-30', 'NotInTheSystem', 'P', -1, 'No Match found', 0)
, ('ALL NULLS', NULL,NULL,NULL,NULL,NULL,-1, 'No Match found',0)
;

-- STACK THE RESULTS AND RETURN THEM.  THIS FUNCTION CAN THEN BE USED
-- TO RUN A QUERY DURING DEPLOY TIME IF TEST_RESULTS != PASSED
-- THEN DON'T DEPLOY THE PRODUCTION CODE
RETURN QUERY
SELECT t.test_name
     , CASE WHEN t.assert1 = results.id
             AND t.assert2 = results.decision
             AND t.assert3 = results.score
            THEN 'PASSED'
            ELSE 'FAILED'
        END::VARCHAR AS test_results
FROM test_temp t, person_match(t.arg1, t.arg2, t.arg3, t.arg4, t.arg5) results;

END $$;

SELECT * FROM test_person_match();