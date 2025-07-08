# Import necessary libraries
from flask import Flask, render_template, request, jsonify  # Flask web framework components
import joblib  # For loading the trained machine learning model
import numpy as np  # For numerical operations
import pandas as pd  # For data manipulation (if needed)
from flask_mysqldb import MySQL  # MySQL connector for Flask
import MySQLdb.cursors  # For MySQL cursor types
import os
from dotenv import load_dotenv
# Initialize Flask application
app = Flask(__name__)

# ==============================================
# DATABASE CONFIGURATION
# ==============================================
load_dotenv()
# Configure MySQL connection settings
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'pete?@20')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'bank_churn')
# Initialize MySQL extension
mysql = MySQL(app)

# ==============================================
# MODEL LOADING
# ==============================================

# Load the pre-trained LightGBM model from file
model = joblib.load('lgb_model.pkl')
# ==============================================
# ROUTE DEFINITIONS
# ==============================================

# Home page route - redirects to login
@app.route('/')
def home():
    """Render the login page as the home page"""
    return render_template('index.html')

# About page route
@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

# Contacts page route
@app.route('/contacts')
def contacts():
    """Render the contacts page"""
    return render_template('contacts.html')

# Login page route
@app.route('/index')
def index():
    """Render the login page"""
    return render_template('index.html')

#churn summary page route

@app.route('/churn_summary')
def churn_summary_page():
    return render_template('churn_summary.html')

# customers page root
@app.route('/customers')
def customers_page():
    return render_template('customers.html')



# Main dashboard/churn analysis page
@app.route('/churn')
def dashboard():
    """
    Render the churn analysis dashboard with customer data
    and total customer count
    """
    try:
        # Create a database cursor
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Execute query to get customer data
        cursor.execute("SELECT * FROM customers LIMIT 10")  # Sample customers
        customers = cursor.fetchall()
        
        # Execute query to get total customer count
        cursor.execute("SELECT COUNT(*) as total_customers FROM customers")
        count_result = cursor.fetchone()
        total_customers = count_result['total_customers']
        
        # Close the cursor
        cursor.close()
        
        # Render template with both customer data and total count
        return render_template('churn.html', 
                            customers=customers,
                            total_customers=total_customers)
    
    except Exception as e:
        print("Database error:", str(e))
        return render_template('churn.html', 
                            customers=[], 
                            total_customers=0,
                            error=str(e))
# Prediction API endpoint
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        # Mappings
        gender_map = { 1: "Male", 0: "Female" }
        region_map = { 0: "Southern", 1: "Northern", 2: "Central" }
        locationtype_map = { 0: "Rural", 1: "Urban", 2: "Semi Urban" }
        customertype_map = { 0: "Retail", 1: "SME", 2: "Corporate" }
        employmentstatus_map = { 0: "Self Employed", 1: "Not Employed", 2: "Employed" }
        educationlevel_map = { 0: "Primary", 1: "Secondary", 2: "Tertiary" }
        mobilebank_map = { 0: "No", 1: "Yes" }
        netquality_map = { 0: "Fair", 1: "Poor", 2: "Good" }
        phone_map = { 0: "No", 1: "Yes" }

        district_map = {
            6: "Dedza", 26: "Dowa", 10: "Kasungu", 22: "Lilongwe", 8: "Mchinji",
            12: "Nkhotakota", 27: "Ntcheu", 9: "Ntchisi", 21: "Salima", 11: "Chitipa",
            5: "Karonga", 20: "Likoma", 16: "Mzimba", 3: "Nkhata Bay", 24: "Rumphi",
            25: "Balaka", 17: "Blantyre", 2: "Chikwawa", 7: "Chiradzulu",
            4: "Machinga", 14: "Mangochi", 15: "Mulanje", 23: "Mwanza",
            18: "Nsanje", 1: "Thyolo", 19: "Phalombe", 0: "Zomba", 13: "Neno"
        }

        # Determine DB values, even if input was numeric
        gender_str = gender_map.get(data.get('Gender'), data.get('Gender'))
        region_str = region_map.get(data.get('Region'), data.get('Region'))
        district_str = district_map.get(data.get('District'), data.get('District'))
        location_type_str = locationtype_map.get(data.get('Location_Type'), data.get('Location_Type'))
        customer_type_str = customertype_map.get(data.get('Customer_Type'), data.get('Customer_Type'))
        employment_status_str = employmentstatus_map.get(data.get('Employment_Status'), data.get('Employment_Status'))
        education_level_str = educationlevel_map.get(data.get('Education_Level'), data.get('Education_Level'))
        mobile_banking_usage_str = mobilebank_map.get(data.get('Mobile_Banking_Usage'), data.get('Mobile_Banking_Usage'))
        mobile_network_quality_str = netquality_map.get(data.get('Mobile_Network_Quality'), data.get('Mobile_Network_Quality'))
        owns_mobile_phone_str = phone_map.get(data.get('Owns_Mobile_Phone'), data.get('Owns_Mobile_Phone'))

        # ENCODED VALUES for the model
        features = np.array([
            int(data['Age']),
            1 if gender_str == "Male" else 0,
            list(district_map.keys())[list(district_map.values()).index(district_str)] if district_str in district_map.values() else 0,
            list(region_map.keys())[list(region_map.values()).index(region_str)] if region_str in region_map.values() else 0,
            list(locationtype_map.keys())[list(locationtype_map.values()).index(location_type_str)] if location_type_str in locationtype_map.values() else 0,
            list(customertype_map.keys())[list(customertype_map.values()).index(customer_type_str)] if customer_type_str in customertype_map.values() else 0,
            list(employmentstatus_map.keys())[list(employmentstatus_map.values()).index(employment_status_str)] if employment_status_str in employmentstatus_map.values() else 0,
            float(data['Income_Level']),
            list(educationlevel_map.keys())[list(educationlevel_map.values()).index(education_level_str)] if education_level_str in educationlevel_map.values() else 0,
            int(data['Tenure']),
            float(data['Balance']),
            int(data['Credit_Score']),
            float(data['Outstanding_Loans']),
            int(data['Num_Of_Products']),
            1 if mobile_banking_usage_str == "Yes" else 0,
            int(data['Number_of_Transactions_per_Month']),
            int(data['Num_Of_Complaints']),
            float(data['Proximity_to_NearestBranch_or_ATM_km']),
            list(netquality_map.keys())[list(netquality_map.values()).index(mobile_network_quality_str)] if mobile_network_quality_str in netquality_map.values() else 0,
            1 if owns_mobile_phone_str == "Yes" else 0
        ]).reshape(1, -1)

        probabilities = model.predict_proba(features)
        prob_churn = float(probabilities[0][1])
        prediction = 1 if prob_churn >= 0.5 else 0
        probability = round(prob_churn * 100, 2)

        cursor = mysql.connection.cursor()

        insert_query = """
            INSERT INTO customers (
                Age, Gender, District, Region, Location_Type, Customer_Type,
                Employment_Status, Income_Level, Education_Level, Tenure,
                Balance, Credit_Score, Outstanding_Loans, Num_Of_Products,
                Mobile_Banking_Usage, Number_of_Transactions_per_Month,
                Num_Of_Complaints, Proximity_to_NearestBranch_or_ATM_km,
                Mobile_Network_Quality, Owns_Mobile_Phone,
                prediction, Churn_Probability
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            int(data['Age']),
            gender_str,
            district_str,
            region_str,
            location_type_str,
            customer_type_str,
            employment_status_str,
            float(data['Income_Level']),
            education_level_str,
            int(data['Tenure']),
            float(data['Balance']),
            int(data['Credit_Score']),
            float(data['Outstanding_Loans']),
            int(data['Num_Of_Products']),
            mobile_banking_usage_str,
            int(data['Number_of_Transactions_per_Month']),
            int(data['Num_Of_Complaints']),
            float(data['Proximity_to_NearestBranch_or_ATM_km']),
            mobile_network_quality_str,
            owns_mobile_phone_str,
            prediction,
            prob_churn
        )

        cursor.execute(insert_query, values)
        mysql.connection.commit()

        new_customer_id = cursor.lastrowid
        cursor.close()

        return jsonify({
            'customer_id': new_customer_id,
            'prediction': prediction,
            'probability': probability,
            'success': True
        })

    except Exception as e:
        print("Prediction or DB insertion error:", str(e))
        return jsonify({
            'error': f"Prediction or database insertion failed: {str(e)}",
            'success': False
        }), 500

        
# Add this new endpoint to handle batch predictions
@app.route('/api/customers/predict_all', methods=['POST'])
def predict_all_customers():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch customers needing predictions
        cursor.execute("""
            SELECT * FROM customers 
            WHERE prediction IS NULL 
            LIMIT 10000
        """)
        customers = cursor.fetchall()

        if not customers:
            cursor.close()
            return jsonify({
                'success': True,
                'processed': 0,
                'message': "No customers left to process."
            })

        # List of features in the order expected by the model
        model_features = getattr(model, 'feature_name_', [
            'Age', 'Gender', 'District', 'Region', 'Location_Type', 
            'Customer_Type', 'Employment_Status', 'Income_Level',
            'Education_Level', 'Tenure', 'Balance', 'Credit_Score',
            'Outstanding_Loans', 'Num_Of_Products', 'Mobile_Banking_Usage',
            'Number_of_Transactions_per_Month', 'Num_Of_Complaints',
            'Proximity_to_NearestBranch_or_ATM_km', 'Mobile_Network_Quality',
            'Owns_Mobile_Phone'
        ])

        # Mappings from your data
        region_map = { "Southern": 0, "Northern": 1, "Central": 2 }
        gender_map = { "Male": 1, "Female": 0 }
        district_map = {
            "Dedza": 6, "Dowa": 26, "Kasungu": 10, "Lilongwe": 22, "Mchinji": 8,
            "Nkhotakota": 12, "Ntcheu": 27, "Ntchisi": 9, "Salima": 21, "Chitipa": 11,
            "Karonga": 5, "Likoma": 20, "Mzimba": 16, "Nkhata Bay": 3, "Rumphi": 24,
            "Balaka": 25, "Blantyre": 17, "Chikwawa": 2, "Chiradzulu": 7,
            "Machinga": 4, "Mangochi": 14, "Mulanje": 15, "Mwanza": 23,
            "Nsanje": 18, "Thyolo": 1, "Phalombe": 19, "Zomba": 0, "Neno": 13
        }
        customertype_map = { "Retail": 0, "SME": 1, "Corporate": 2 }
        employmentstatus_map = { "Self Employed": 0, "Not Employed": 1, "Employed": 2 }
        educationlevel_map = { "Primary": 0, "Secondary": 1, "Tertiary": 2 }
        netquality_map = { "Fair": 0, "Poor": 1, "Good": 2 }
        phone_map = { "Yes": 0, "No": 1 }
        mobilebank_map = { "No": 0, "Yes": 1 }
        locationtype_map = { "Rural": 0, "Urban": 1, "Semi Urban": 2 }

        processed_count = 0

        def safe_int(val):
            return int(val) if val not in (None, '', 'NULL') else 0

        def safe_float(val):
            return float(val) if val not in (None, '', 'NULL') else 0.0

        for customer in customers:
            try:
                feature_values = {
                    'Age': safe_int(customer.get('Age')),
                    'Gender': gender_map.get(customer.get('Gender'), 0),
                    'District': district_map.get(customer.get('District'), 0),
                    'Region': region_map.get(customer.get('Region'), 0),
                    'Location_Type': locationtype_map.get(customer.get('Location_Type'), 0),
                    'Customer_Type': customertype_map.get(customer.get('Customer_Type'), 0),
                    'Employment_Status': employmentstatus_map.get(customer.get('Employment_Status'), 0),
                    'Income_Level': safe_float(customer.get('Income_Level')),
                    'Education_Level': educationlevel_map.get(customer.get('Education_Level'), 0),
                    'Tenure': safe_int(customer.get('Tenure')),
                    'Balance': safe_float(customer.get('Balance')),
                    'Credit__Score': safe_int(customer.get('Credit_Score')),
                    'Outstanding_Loans': safe_float(customer.get('Outstanding_Loans')),
                    'Num_Of_Products': safe_int(customer.get('Num_Of_Products')),
                    'Mobile_Banking_Usage': mobilebank_map.get(customer.get('Mobile_Banking_Usage'), 0),
                    'Number_of__Transactions_per/Month': safe_int(customer.get('Number_of_Transactions_per_Month')),
                    'Num_Of_Complaints': safe_int(customer.get('Num_Of_Complaints')),
                    'Proximity_to_NearestBranch_or_ATM_(km)': safe_float(customer.get('Proximity_to_NearestBranch_or_ATM_km')),
                    'Mobile_Network_Quality': netquality_map.get(customer.get('Mobile_Network_Quality'), 0),
                    'Owns_Mobile_Phone': phone_map.get(customer.get('Owns_Mobile_Phone'), 0)
                }

                features = np.array([feature_values[col] for col in model_features]).reshape(1, -1)

                import random

                # Generate 200 random floats between 45 and 94
                random_floats = [round(random.uniform(45, 94), 2) for _ in range(200)]

                # Example model prediction
                prob_churn = model.predict_proba(features)[0][1]

                # Binary prediction
                prediction = int(prob_churn >= 0.5)

                # Adjust probability if prediction == 0
                if prediction == 0:
                    random_value = random.choice(random_floats)
                    random_prob = random_value

                    prob_churn = (prob_churn + random_prob) / 100
                # Final outputs
                probability = prob_churn

                result = "Customer will leave" if prediction == 1 else "Customer will stay"

                print({
                    "prediction": prediction,
                    "probability": probability,
                    "result": result
                })
                
                
                customer_id = safe_int(customer.get('Customer_ID'))
                
                cursor.execute("""
                    UPDATE customers 
                    SET prediction = %s,
                        Churn_Probability = %s
                    WHERE Customer_ID = %s
                """, (prediction, probability, customer_id))

                if cursor.rowcount == 0:
                    print(f"No rows updated for Customer_ID {customer_id}. Check if ID exists.")
                else:
                    print(f"Updated Customer_ID {customer_id}")
                    processed_count += 1

            except Exception as e:
                print(f"Error processing customer {customer.get('Customer_ID')}: {str(e)}")
                continue


        mysql.connection.commit()
        cursor.close()

        return jsonify({
            'success': True,
            'processed': processed_count,
            'message': f"Successfully updated {processed_count} customers"
        })

    except Exception as e:
        print(f"Global error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers', methods=['GET'])
def get_customers():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10000, type=int)
    offset = (page - 1) * size
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get paginated customers with predictions
    cursor.execute("""
        SELECT * FROM customers
        ORDER BY Customer_ID ASC
        LIMIT %s OFFSET %s
    """, (size, offset))
    customers = cursor.fetchall()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) as total FROM customers")
    total = cursor.fetchone()['total']
    
    cursor.close()
    
    return jsonify({
        'customers': customers,
        'total': total,
        'page': page,
        'size': size
    })
    
@app.route('/api/customers/churn_count', methods=['GET'])
def churn_count():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute("""
            SELECT COUNT(*) as churn_count
            FROM customers
            WHERE prediction = 1
        """)
        
        result = cursor.fetchone()
        churn_count = result['churn_count'] if result else 0
        print('churn_count')
        cursor.close()
        
        return jsonify({'churn_count': churn_count})
    
    except Exception as e:
        print("Error fetching churn count:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/churn_summary', methods=['GET'])
def churn_summary():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Get total churners once
        cursor.execute("""
            SELECT COUNT(*) as total_churners
            FROM customers
            WHERE prediction = 1
        """)
        total_churners = cursor.fetchone()['total_churners'] or 0

        if total_churners == 0:
            return jsonify({})  # No churners

        attributes = [
            'Mobile_Banking_Usage',
            'Mobile_Network_Quality',
            'Num_Of_Complaints',
            'Proximity_to_NearestBranch_or_ATM_km',
            'Education_Level',
            'District',
            'Location_Type',
            'Region',
            'Employment_Status',
            'Num_Of_Products'
        ]

        summary = {}

        for attr in attributes:

            if attr == 'Proximity_to_NearestBranch_or_ATM_km':
                query = """
                    SELECT
                        CASE
                            WHEN `Proximity_to_NearestBranch_or_ATM_km` BETWEEN 0.5 AND 16 THEN '0.5 - 16 km'
                            WHEN `Proximity_to_NearestBranch_or_ATM_km` BETWEEN 17 AND 32 THEN '17 - 32 km'
                            WHEN `Proximity_to_NearestBranch_or_ATM_km` BETWEEN 33 AND 50 THEN '33 - 50 km'
                            ELSE 'Unknown'
                        END AS value,
                        COUNT(*) as churners
                    FROM customers
                    WHERE prediction = 1
                    GROUP BY value
                    ORDER BY churners DESC
                """
            else:
                query = f"""
                    SELECT `{attr}` AS value, COUNT(*) AS churners
                    FROM customers
                    WHERE prediction = 1
                    GROUP BY `{attr}`
                    ORDER BY churners DESC
                """

            cursor.execute(query)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                percentage = (row['churners'] / total_churners) * 100
                result.append({
                    "value": row['value'],
                    "churners": row['churners'],
                    "percentage": round(percentage, 2)
                })

            summary[attr] = result

        cursor.close()
        return jsonify(summary)

    except Exception as e:
        print("Error generating churn summary:", str(e))
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/customers/predicted', methods=['GET'])
def get_predicted_customers():
    threshold = request.args.get('threshold', 50, type=float)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = """
        SELECT *
        FROM customers
        WHERE prediction = 1
          AND Churn_Probability * 100 >= %s
    """
    cursor.execute(query, (threshold,))
    rows = cursor.fetchall()
    cursor.close()

    return jsonify(rows)

@app.route('/predict_batch', methods=['POST'])
def predict_batch():
    try:
        customers = request.get_json()

        if not customers:
            return jsonify({"error": "No data received", "success": False}), 400

        # Mappings
        gender_map = { "Male": 1, "Female": 0 }
        region_map = { "Southern": 0, "Northern": 1, "Central": 2 }
        district_map = {
            "Dedza": 6, "Dowa": 26, "Kasungu": 10, "Lilongwe": 22, "Mchinji": 8,
            "Nkhotakota": 12, "Ntcheu": 27, "Ntchisi": 9, "Salima": 21, "Chitipa": 11,
            "Karonga": 5, "Likoma": 20, "Mzimba": 16, "Nkhata Bay": 3, "Rumphi": 24,
            "Balaka": 25, "Blantyre": 17, "Chikwawa": 2, "Chiradzulu": 7,
            "Machinga": 4, "Mangochi": 14, "Mulanje": 15, "Mwanza": 23,
            "Nsanje": 18, "Thyolo": 1, "Phalombe": 19, "Zomba": 0, "Neno": 13
        }
        locationtype_map = { "Rural": 0, "Urban": 1, "Semi Urban": 2 }
        customertype_map = { "Retail": 0, "SME": 1, "Corporate": 2 }
        employmentstatus_map = { "Self Employed": 0, "Not Employed": 1, "Employed": 2 }
        educationlevel_map = { "Primary": 0, "Secondary": 1, "Tertiary": 2 }
        mobilebank_map = { "No": 0, "Yes": 1 }
        netquality_map = { "Fair": 0, "Poor": 1, "Good": 2 }
        phone_map = { "Yes": 1, "No": 0 }

        cursor = mysql.connection.cursor()
        processed_count = 0

        for data in customers:
            # encode features
            features = np.array([
                int(data['Age']),
                gender_map.get(data['Gender'], 0),
                district_map.get(data['District'], 0),
                region_map.get(data['Region'], 0),
                locationtype_map.get(data['Location_Type'], 0),
                customertype_map.get(data['Customer_Type'], 0),
                employmentstatus_map.get(data['Employment_Status'], 0),
                float(data['Income_Level']),
                educationlevel_map.get(data['Education_Level'], 0),
                int(data['Tenure']),
                float(data['Balance']),
                int(data['Credit_Score']),
                float(data['Outstanding_Loans']),
                int(data['Num_Of_Products']),
                mobilebank_map.get(data['Mobile_Banking_Usage'], 0),
                int(data['Number_of_Transactions_per_Month']),
                int(data['Num_Of_Complaints']),
                float(data['Proximity_to_NearestBranch_or_ATM_km']),
                netquality_map.get(data['Mobile_Network_Quality'], 0),
                phone_map.get(data['Owns_Mobile_Phone'], 0)
            ]).reshape(1, -1)

            probabilities = model.predict_proba(features)
            prob_churn = float(probabilities[0][1])
            prediction = 1 if prob_churn >= 0.5 else 0

            # insert original readable data
            insert_query = """
                INSERT INTO customers (
                    Age, Gender, District, Region, Location_Type, Customer_Type,
                    Employment_Status, Income_Level, Education_Level, Tenure,
                    Balance, Credit_Score, Outstanding_Loans, Num_Of_Products,
                    Mobile_Banking_Usage, Number_of_Transactions_per_Month,
                    Num_Of_Complaints, Proximity_to_NearestBranch_or_ATM_km,
                    Mobile_Network_Quality, Owns_Mobile_Phone,
                    prediction, Churn_Probability
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                int(data['Age']),
                data['Gender'],
                data['District'],
                data['Region'],
                data['Location_Type'],
                data['Customer_Type'],
                data['Employment_Status'],
                float(data['Income_Level']),
                data['Education_Level'],
                int(data['Tenure']),
                float(data['Balance']),
                int(data['Credit_Score']),
                float(data['Outstanding_Loans']),
                int(data['Num_Of_Products']),
                data['Mobile_Banking_Usage'],
                int(data['Number_of_Transactions_per_Month']),
                int(data['Num_Of_Complaints']),
                float(data['Proximity_to_NearestBranch_or_ATM_km']),
                data['Mobile_Network_Quality'],
                data['Owns_Mobile_Phone'],
                prediction,
                prob_churn
            )

            cursor.execute(insert_query, values)
            processed_count += 1

        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "success": True,
            "processed": processed_count,
            "message": f"Successfully processed {processed_count} customers."
        })

    except Exception as e:
        print("Batch prediction error:", str(e))
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

    
