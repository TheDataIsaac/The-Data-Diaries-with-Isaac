DROP TABLE IF EXISTS foiaData;
CREATE TABLE foiaData (
    AsOfDate                DATE,
    Program                	CHAR(2),
    BorrName                VARCHAR(255),
    BorrStreet              VARCHAR(100),
    BorrCity                VARCHAR(100),
    BorrState               CHAR(2),
    BorrZip                 INTEGER,
    BankName                VARCHAR(255),
    BankStreet              VARCHAR(100),
    BankCity                VARCHAR(50),
    BankState               CHAR(2),
    BankZip                 INTEGER,
    GrossApproval           INTEGER,
    SBAGuaranteedApproval   FLOAT,
    ApprovalDate            DATE,
    ApprovalFiscalYear      SMALLINT,
    FirstDisbursementDate   DATE,
    DeliveryMethod          VARCHAR(20),
    subpgmdesc              VARCHAR(50),
    InitialInterestRate     FLOAT,
    TermInMonths            INTEGER,
    NaicsCode               FLOAT,
    NaicsDescription        VARCHAR(255),
    ProjectCounty           VARCHAR(50),
    ProjectState            CHAR(2),
    SBADistrictOffice       VARCHAR(50),
    CongressionalDistrict  	FLOAT,
    BusinessType            VARCHAR(20),
    LoanStatus              VARCHAR(10),
    PaidInFullDate          DATE,
    ChargeOffDate           DATE,
    GrossChargeOffAmount    INTEGER,
    RevolverStatus          SMALLINT,
    JobsSupported           SMALLINT,
    HasFranchise            SMALLINT
);


-- To copy the data from the CovidDeaths.csv file into the database table
--SHOW server_encoding;
--SHOW client_encoding;
--SET client_encoding TO 'UTF8';
--\copy foiaData FROM '/Users/ORESANYA/Classic Isaac/Git/The-Data-Diaries-with-Isaac/Dataset Analysis/FOIA Data Analysis/foiaData.csv' WITH (FORMAT CSV,HEADER);

-- Display the first 20 rows from the table
SELECT * FROM foiaData LIMIT 20;

-- Display the count of rows in the table
SELECT COUNT(*) FROM foiaData;

-- Calculate the distribution of loan statuses in terms of count and percentage
SELECT loanstatus, 
    COUNT(loanstatus) AS loan_status_count,
    ROUND(COUNT(loanstatus) * 100.0 / SUM(COUNT(loanstatus)) OVER (), 2) AS percentage
FROM foiaData
GROUP BY loanstatus;

-- List banks with the highest number of approved loans
SELECT bankname, COUNT(bankname) AS approved_loans_count
FROM foiaData 
GROUP BY bankname
ORDER BY approved_loans_count DESC;

-- Calculate the median loan approval amount for each project state
SELECT projectstate, 
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY grossapproval) AS median_loan_approval_amount
FROM foiaData
GROUP BY projectstate
ORDER BY median_loan_approval_amount DESC;

-- Calculate the average interest rate for each business type
SELECT businesstype,
    ROUND(CAST (AVG(initialinterestrate) AS numeric),2) AS avg_interest_rate
FROM foiaData
GROUP BY businesstype;

-- Calculate the median loan approval amount for different term durations in months
SELECT TermInMonths, 
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY grossapproval) AS median_approval_amount
FROM foiaData
GROUP BY TermInMonths;

-- Calculate the count of approved loans for each fiscal year
SELECT approvalfiscalyear, 
   COUNT(approvalfiscalyear) AS approved_loan_count
FROM foiaData
GROUP BY approvalfiscalyear
ORDER BY approvalfiscalyear;

-- Calculate the most common loan delivery methods and subprograms
SELECT deliverymethod, 
    COUNT(deliverymethod) AS count
FROM foiaData
GROUP BY deliverymethod 
ORDER BY count DESC;

-- Calculate the average approval amount for each delivery method
SELECT deliverymethod, 
    ROUND(AVG(grossapproval)) AS average_approval_amount
FROM foiaData
GROUP BY deliverymethod
ORDER BY COUNT(deliverymethod) DESC;

-- Calculate the charge-off rates across different business types
SELECT businesstype, 
    COUNT(loanstatus) AS charge_off_count
FROM foiaData 
WHERE loanstatus = 'CHGOFF'
GROUP BY businesstype;

-- List top borrowers by total loan amount approved
SELECT borrname, 
    COUNT(borrname) AS borrower_count, 
    SUM(sbaguaranteedapproval) AS total_sba_approval_amount
FROM foiaData
GROUP BY borrname
ORDER BY borrower_count DESC;

-- Calculate loan amount distribution by borrower's state
SELECT borrstate, 
   MIN(grossapproval) AS min_loan_amount, 
   MAX(grossapproval) AS max_loan_amount, 
   ROUND(AVG(grossapproval)) AS avg_loan_amount
FROM foiaData
GROUP BY borrstate;

-- Calculate average loan amount by state and business type
SELECT projectstate, businesstype, 
   ROUND(AVG(grossapproval)) AS avg_loan_amount
FROM foiaData
GROUP BY projectstate, businesstype;

-- List top borrowers by total SBA guarantee amount
SELECT borrname, 
   SUM(sbaguaranteedapproval) AS total_sba_approval_amount
FROM foiaData
GROUP BY borrname
ORDER BY total_sba_approval_amount DESC
LIMIT 10;

-- Calculate the average interest rate for each loan status
SELECT loanstatus, 
   ROUND(CAST (AVG(initialinterestrate) AS numeric),2) AS avg_interest_rate
FROM foiaData
GROUP BY loanstatus;

-- List top NAICS codes by loan count
SELECT naicscode, naicsdescription, 
   COUNT(naicscode) AS loan_count
FROM foiaData
GROUP BY naicscode, naicsdescription
ORDER BY loan_count DESC
LIMIT 10;

-- Calculate loan count by delivery method and business type
SELECT deliverymethod, businesstype, 
   COUNT(*) AS loan_count
FROM foiaData
GROUP BY deliverymethod, businesstype;

-- Calculate loan count by subprogram and loan status
SELECT subpgmdesc, loanstatus, 
   COUNT(*) AS loan_count
FROM foiaData
GROUP BY subpgmdesc, loanstatus;

-- Calculate the total number of jobs supported according to the foiaData table
SELECT SUM(jobssupported) FROM foiaData;



