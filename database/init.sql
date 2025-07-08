-- SQL script to initialize the 'bank_churn' database and 'customers' table
CREATE DATABASE IF NOT EXISTS bank_churn;
USE bank_churn;

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Age INT,
    Gender VARCHAR(10),
    District VARCHAR(50),
    Region VARCHAR(50),
    Location_Type VARCHAR(20),
    Customer_Type VARCHAR(20),
    Employment_Status VARCHAR(20),
    Income_Level FLOAT,
    Education_Level VARCHAR(20),
    Tenure INT,
    Balance FLOAT,
    Credit_Score INT,
    Outstanding_Loans FLOAT,
    Num_Of_Products INT,
    Mobile_Banking_Usage VARCHAR(5),
    Number_of_Transactions_per_Month INT,
    Num_Of_Complaints INT,
    Proximity_to_NearestBranch_or_ATM_km FLOAT,
    Mobile_Network_Quality VARCHAR(10),
    Owns_Mobile_Phone VARCHAR(5),
    prediction TINYINT,
    Churn_Probability FLOAT
); 

-- Sample data for the 'customers' table
INSERT INTO customers (
    Age, Gender, District, Region, Location_Type, Customer_Type,
    Employment_Status, Income_Level, Education_Level, Tenure,
    Balance, Credit_Score, Outstanding_Loans, Num_Of_Products,
    Mobile_Banking_Usage, Number_of_Transactions_per_Month,
    Num_Of_Complaints, Proximity_to_NearestBranch_or_ATM_km,
    Mobile_Network_Quality, Owns_Mobile_Phone,
    prediction, Churn_Probability
) VALUES
(35, 'Male', 'Lilongwe', 'Central', 'Urban', 'Retail', 'Employed', 50000.00, 'Tertiary', 5, 20000.00, 700, 10000.00, 2, 'Yes', 15, 1, 2.5, 'Good', 'Yes', 1, 85.50),
(28, 'Female', 'Blantyre', 'Southern', 'Urban', 'SME', 'Self Employed', 30000.00, 'Secondary', 3, 12000.00, 650, 5000.00, 1, 'No', 8, 0, 5.0, 'Fair', 'Yes', 0, 40.25),
(42, 'Male', 'Mzimba', 'Northern', 'Rural', 'Corporate', 'Employed', 80000.00, 'Tertiary', 10, 50000.00, 750, 20000.00, 3, 'Yes', 20, 2, 10.0, 'Good', 'No', 1, 67.80),
(31, 'Female', 'Mangochi', 'Southern', 'Semi Urban', 'Retail', 'Not Employed', 15000.00, 'Primary', 2, 3000.00, 600, 2000.00, 1, 'No', 5, 1, 1.2, 'Poor', 'Yes', 0, 25.00); 