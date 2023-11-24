SET search_path TO freelancer;

DROP TABLE freelancerdata;

CREATE TABLE freelancerdata (
    job_title VARCHAR(500),
    projectId INT,
    job_description TEXT,
    tags TEXT, 
    client_state VARCHAR(50),
    client_country VARCHAR(50),
    client_average_rating FLOAT,
    client_review_count INTEGER,
    min_price DECIMAL(10, 2),
    max_price DECIMAL(10, 2),
	avg_price DECIMAL(10, 2),
    currency VARCHAR(3),
    rate_type VARCHAR(10)
);

--SHOW server_encoding;
--SHOW client_encoding;
--SET client_encoding TO 'UTF8';

-- Load data into the freelancerdata table from a CSV file
-- \copy freelancerdata FROM 'C:/Users/ORESANYA/Classic Isaac/Git/The-Data-Diaries-with-Isaac/Dataset Analysis/Freelancer Job Postings Data Analysis/freelancerresult.csv' WITH (FORMAT CSV,HEADER);

ALTER TABLE freelancerdata ALTER COLUMN tags TYPE TEXT[] USING translate(tags,'[]''','{}')::TEXT[];



-- Count pairs of skills, ordered by frequency, and limit to the top 20
SELECT skill1, skill2, COUNT(*) AS pair_count
FROM (
  SELECT tags[i] AS skill1, tags[j] AS skill2
  FROM freelancerdata, generate_series(1, ARRAY_LENGTH(tags, 1)) AS i, generate_series(1, ARRAY_LENGTH(tags, 1)) AS j
  WHERE i < j
) AS pairs
GROUP BY skill1, skill2
ORDER BY pair_count DESC
LIMIT 20;

-- Calculate median price and frequency for different currency-rate_type combinations
SELECT currency, rate_type,
	PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY avg_price) AS median_price,
	COUNT(rate_type) AS frequency
FROM freelancerdata GROUP BY currency, rate_type ORDER BY frequency DESC;

-- Count jobs for each currency and order by count in descending order
SELECT currency, COUNT(*) AS count FROM freelancerdata GROUP BY currency ORDER BY count DESC;

-- Categorize client ratings and count the occurrences for each category
WITH cfield AS (SELECT
  client_average_rating,
  CASE
	WHEN client_average_rating >= 4.5 THEN '5'
	WHEN client_average_rating >= 3.5 AND client_average_rating < 4.5 THEN '4'
	WHEN client_average_rating >= 2.5 AND client_average_rating < 3.5 THEN '3'
	WHEN client_average_rating >= 1.5 AND client_average_rating < 2.5 THEN '2'
	WHEN client_average_rating >= 0.5 AND client_average_rating < 1.5 THEN '1'
	ELSE 'No rating'
  END AS rating_category
FROM
  freelancerdata)
SELECT rating_category, COUNT(*) AS count FROM cfield
GROUP BY rating_category ORDER BY count DESC;
  

-- Count frequencies of project types excluding specific ones and filter by certain project types
SELECT * FROM 
(
    SELECT project_type, COUNT(*) AS frequency FROM 
    (
        SELECT UNNEST(tags) AS project_type FROM freelancerdata
    ) as unnested_data
    WHERE project_type != 'data analysis' AND project_type != 'data analytics'
    GROUP BY project_type
    ORDER BY frequency DESC
) as project_type_table
WHERE (project_type ILIKE ANY (ARRAY['data%', '%analysis%', 'machine learning (ml)', '%scraping%', '%research%', 'report writing', 'statistical modeling', 'biostatistics', 'regression testing', 'etl']));

  
-- Categorize skills and count the occurrences for each category
SELECT * FROM 
(
    SELECT 
        CASE 
            WHEN skills ILIKE '%excel%' THEN 'excel'
            WHEN skills ILIKE '%sql%' THEN 'sql'
            ELSE skills
        END AS categorized_skills,
        COUNT(*) AS frequency 
    FROM 
    (
        SELECT UNNEST(tags) AS skills FROM freelancerdata
    ) as unnested_data
    GROUP BY categorized_skills
    ORDER BY frequency DESC
) as skills_table
WHERE categorized_skills ILIKE ANY (ARRAY['excel', 'sql', 'python', 'tableau', 'power bi', 'r %', 'sas', 'powerpoint', 'word', 'azure', 'oracle', 'sap', 'aws', 'go', 'flow', '%vba%', 'snowflake', 'java', 'looker', ' qlik', 'spark', 'sas' ]);

-- Count the number of jobs for each client country and order by count in descending order 
SELECT client_country, COUNT(*) AS job_count
FROM freelancerdata
GROUP BY client_country
ORDER BY job_count DESC;