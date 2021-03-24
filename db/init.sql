CREATE TABLE humans (
    id SERIAL PRIMARY KEY,
    given_name VARCHAR(256),
    family_name VARCHAR(256),
    email_address VARCHAR(320),
    date_of_birth DATE,
    gender CHAR(1)  -- 'M','F','X'
);


-- SQL QUESTION 1: CREATE A STORED PROCEDURE TO MATCH A USER
CREATE OR REPLACE FUNCTION person_match(
    IN f_name    VARCHAR,
    IN l_name    VARCHAR,
    IN dob       DATE,
    IN email     VARCHAR,
    IN p_gender  CHAR
)

-- RESULTS RETURNED IN A TABLE FORM.  COULD CHOOSE TO RETURN
-- AS OUT VARIABLES IF THE USE CASE ALLOWS
-- LEAVING AS TABLE IN CASE USE CASE IS TO RETURN ALL POSSIBLE
-- RESULTS (IF MORE THAN ONE MATCH EXISTS ON FIRST,LAST,DOB,EMAIL
RETURNS TABLE (
  id       INT,
  decision VARCHAR,
  score    FLOAT
)

LANGUAGE PLPGSQL
AS $$
DECLARE
    found_humans humans%rowtype;
    id           INT;
    decision     VARCHAR;
    score        FLOAT := 0;

BEGIN
-- GET MATCHES: REQUIREMENT IS MATCH ON FIRST,LAST,EMAIL
-- AND AT LEAST ONE OF: DOB AND GENDER
   SELECT h.*
    INTO found_humans
    FROM humans h
   WHERE h.given_name = f_name
     AND h.family_name = l_name
     AND h.email_address = email
     AND (
          h.date_of_birth = dob
           OR
          h.gender = p_gender
         );

-- IF NO MATCH, RETURN SENTINEL -1 FOR ID AND NO MATCH FOUND
    IF NOT FOUND THEN
        id       := -1;
        decision := 'No Match found';
        score    := 0;

-- IF A MATCH IS FOUND, CHECK CONFIDENCE (IF DOB AND GENDER ALSO MATCH)
-- GENDER IS WEIGHTED LOWER THAN DOB BECAUSE A MATCH ON DOB IS MORE RARE
    ELSE
        id := found_humans.id;
        IF found_humans.date_of_birth = dob THEN
            score := score + 0.75;
        END IF;
        IF found_humans.gender = p_gender THEN
            score := score + 0.25;
        END IF;

        IF score >= 1 THEN
            decision := 'Exact Match';
        ELSE
            decision := 'Partial Match';
        END IF;
    END IF;

    RETURN QUERY SELECT id, decision, score;
END $$;