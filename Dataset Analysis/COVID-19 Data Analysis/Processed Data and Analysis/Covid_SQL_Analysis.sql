DROP TABLE CovidDeaths;

CREATE TABLE CovidDeaths (
iso_code VARCHAR(10),
continent VARCHAR(20),
location VARCHAR(50),
date  DATE,
population BIGINT,
total_cases BIGINT,
new_cases BIGINT,
total_deaths BIGINT,
new_deaths BIGINT,
PRIMARY KEY(iso_code,date));


-- To copy the data from the CovidDeaths.csv file into the database table
-- \copy CovidDeaths FROM '/Users/ORESANYA/Classic Isaac/Git/COVID-19-analysis-with-Tableau/Processed Data and Analysis/CovidDeaths.csv' WITH (FORMAT CSV,HEADER);

SELECT * FROM CovidDeaths WHERE location='United States';


CREATE INDEX deaths_loc_idx ON CovidDeaths(location);

-- INCIDENCE RATE
-- total COVID cases compared to the population
SELECT location,date,population,total_cases,(CAST(total_cases AS numeric)/population)*100 cummulative_cases_per_population
FROM CovidDeaths
WHERE location='United States'
ORDER BY date;

-- MORTALITY RATE
-- This metric measures the proportion of people who die as a result of being infected with COVID-19
SELECT location,date,population,total_deaths,(CAST(total_deaths AS numeric)/population)*100 mortality_rate
FROM CovidDeaths
WHERE location='United States'
ORDER BY date;


-- INFECTION FATALITY RATE
-- This metric measures the proportion of deaths among all individuals who are infected with COVID-19 
SELECT location,date,total_cases,total_deaths,(CAST(total_deaths AS numeric)/total_cases)*100 infection_fatality_rate
FROM CovidDeaths
WHERE location='United States'
ORDER BY date;


-- TOP 10 DAYS WITH HIGHEST NUMBER OF NEW COVID-19 CASES
SELECT location,date,new_cases
FROM CovidDeaths
WHERE location='United States'
ORDER BY new_cases DESC
LIMIT 10;

-- MORTALITY RATE PER 100,000
-- This metric measures the number of COVID-19 dedaths per 100,000 people
SELECT location,date,population,total_deaths,(CAST(total_deaths AS numeric)/population)*100000 mortality_rate_per_100000
FROM CovidDeaths
WHERE location='United States'
ORDER BY date;

-- TOTAL DEATH FOR EACH LOCATION
SELECT location,MAX(total_deaths) max_total_deaths
FROM CovidDeaths
GROUP BY location
ORDER BY max_total_deaths DESC;

-- Highest number of new COVID-19 cases reported in a single day for each location
SELECT location, MAX(new_cases) peak_daily_cases FROM CovidDeaths
GROUP BY location ORDER BY peak_daily_cases DESC;

-- Summarizes COVID-19 data by continent
SELECT * FROM CovidDeaths;
WITH continent_location AS (
SELECT continent, location,MAX(population) population, MAX(total_cases) max_total_cases, MAX(total_deaths) max_total_deaths
FROM CovidDeaths
GROUP BY continent, location
ORDER BY max_total_deaths DESC)
SELECT continent,SUM(population) total_population, SUM(max_total_cases) total_cases, SUM(max_total_deaths) total_deaths
FROM continent_location
GROUP BY continent
ORDER BY total_deaths DESC;

-- Total COVID-19 cases by date
SELECT date, SUM(total_cases) total_cases
FROM CovidDeaths
GROUP BY date
ORDER BY date
