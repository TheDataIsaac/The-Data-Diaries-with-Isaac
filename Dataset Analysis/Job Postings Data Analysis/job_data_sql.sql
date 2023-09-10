-- Drop the 'job_data' table
DROP TABLE job_data

-- Create the 'job_data' table
CREATE TABLE job_data (
	job_id TEXT PRIMARY KEY,
    title VARCHAR(255),
    company_name VARCHAR(255),
	city VARCHAR(20),
	state CHAR(2),
    via VARCHAR(255),
    extensions TEXT,
    schedule_type VARCHAR(50),
    work_from_home BOOLEAN,
    search_term VARCHAR(50),
    date DATE,
    search_location VARCHAR(50),
	salary_pay VARCHAR(30),
    salary_rate VARCHAR(10),
    salary_avg NUMERIC(10, 2), 
    salary_min NUMERIC(10, 2),
    salary_max NUMERIC(10, 2),
    salary_standardized NUMERIC(10, 2),
    description_tokens TEXT,
	salary_info_status VARCHAR(15),
	title_group VARCHAR(20)
);


--SHOW server_encoding;
--SHOW client_encoding;
--SET client_encoding TO 'UTF8';

-- Load data into the job_data table from a CSV file
\copy job_data FROM '/Users/ORESANYA/Classic Isaac/Git/The-Data-Diaries-with-Isaac/Dataset Analysis/Job Postings Data Analysis/jobdata_processed_data.csv' WITH (FORMAT CSV,HEADER);

-- Modify the 'extensions' and 'description' columns to be of type TEXT[]
ALTER TABLE job_data ALTER COLUMN extensions TYPE TEXT[] USING translate(extensions,'[]''','{}')::TEXT[];
ALTER TABLE job_data ALTER COLUMN description_tokens TYPE TEXT[] USING translate(description_tokens,'[]''','{}')::TEXT[];

-- Select all data from the 'job_data' table
SELECT * FROM job_data;

-- Count the number of job titles in each 'title_group'
SELECT title_group, COUNT(title_group) FROM job_data
GROUP BY title_group;

-- Count the number of job titles in each 'title_group' and 'state', ordered by the number of job titles
SELECT title_group, state, COUNT(*) AS count
FROM job_data
GROUP BY title_group, state
ORDER BY count DESC;

-- Count the number of job titles in each 'title_group' where 'work_from_home' is true, ordered by job count
SELECT title_group, COUNT(*) as job_count
FROM job_data
WHERE work_from_home = true
GROUP BY title_group
ORDER BY job_count DESC;

-- Count the occurrence of each keyword in job descriptions
SELECT UNNEST(description_tokens) AS keyword, COUNT(*) FROM job_data
GROUP BY keyword
ORDER BY count DESC;

-- Count the occurrence of each keyword in job descriptions within each 'title_group'
SELECT title_group, UNNEST(description_tokens) as keyword, COUNT(*) as keyword_count
FROM job_data
GROUP BY title_group, keyword
ORDER BY title_group, keyword_count DESC;

-- Count the number of job titles in each 'title_group' and 'schedule_type'
SELECT title_group, schedule_type, COUNT(*) as job_count
FROM job_data
GROUP BY title_group, schedule_type
ORDER BY job_count DESC;

-- Count the number of job titles in each 'title_group' where 'salary_info_status' is 'Available' and 'work_from_home' is true
SELECT title_group, COUNT(*) AS job_count
FROM job_data
WHERE salary_info_status = 'Available' AND work_from_home = true
GROUP BY title_group;

-- Count the number of job postings from each company
SELECT company_name, COUNT(company_name) FROM job_data
GROUP BY company_name
ORDER BY count DESC;

-- Count the occurrences of each 'via' value in job postings
SELECT via, COUNT(via) FROM job_data
GROUP BY via
ORDER BY count DESC;

-- Count the number of job postings for each month
SELECT (EXTRACT('month' FROM date)) AS month, COUNT(EXTRACT('month' FROM date))
FROM job_data
GROUP BY month
ORDER BY count DESC;

-- Calculate average, minimum, maximum, and median salary statistics for each state
SELECT state, AVG(salary_standardized) as average_salary, MIN(salary_standardized) as min_salary, MAX(salary_standardized) as max_salary,
PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary_standardized) AS median_salary
FROM job_data WHERE state IS NOT NULL
GROUP BY state;

-- Calculate salary statistics (minimum, maximum, average, median) for each 'title_group' and 'salary_rate'
SELECT title_group, salary_rate, MIN(salary_avg) minimum_salary, MAX(salary_avg) maximum_salary, ROUND(AVG(salary_avg),2) average_salary,
PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary_avg) AS median_salary
FROM job_data
WHERE salary_pay IS NOT NULL
GROUP BY title_group, salary_rate
ORDER BY title_group;

-- Calculate salary statistics (minimum, maximum, average, median) for each 'title_group'
SELECT title_group, MIN(salary_standardized) minimum_salary, MAX(salary_standardized) maximum_salary, ROUND(AVG(salary_standardized),2) average_salary,
PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary_standardized) AS median_salary
FROM job_data
WHERE salary_pay IS NOT NULL
GROUP BY title_group
ORDER BY minimum_salary;

