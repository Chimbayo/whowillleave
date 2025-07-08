from flask import Blueprint, render_template, request, jsonify
from .models import load_model
from .db import get_db_cursor
import numpy as np

main = Blueprint('main', __name__)

model = load_model()

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contacts')
def contacts():
    return render_template('contacts.html')

@main.route('/index')
def index():
    return render_template('index.html')

@main.route('/churn_summary')
def churn_summary_page():
    return render_template('churn_summary.html')

@main.route('/customers')
def customers_page():
    return render_template('customers.html')

@main.route('/churn')
def dashboard():
    try:
        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM customers LIMIT 10")
        customers = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) as total_customers FROM customers")
        count_result = cursor.fetchone()
        total_customers = count_result['total_customers']
        cursor.close()
        return render_template('churn.html', customers=customers, total_customers=total_customers)
    except Exception as e:
        return render_template('churn.html', customers=[], total_customers=0, error=str(e))

# Add all other routes and API endpoints from app.py here, adapting imports as needed.

from flask import current_app
import pandas as pd

@main.route('/predict', methods=['POST'])
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

        cursor = get_db_cursor(dict_cursor=False)
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
            probability
        )
        cursor.execute(insert_query, values)
        cursor.connection.commit()
        cursor.close()

        return jsonify({'prediction': prediction, 'probability': probability})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Repeat for all other API endpoints and error handlers from app.py 

# --- API ENDPOINTS MOVED FROM OLD app.py ---

@main.route('/api/customers', methods=['GET'])
def get_customers():
    print("DEBUG: /api/customers endpoint called")
    try:
        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        cursor.close()
        return jsonify(customers)
    except Exception as e:
        print("DEBUG: Error in /api/customers:", e)
        return jsonify({'error': str(e)}), 500
        

@main.route('/api/customers/churn_count', methods=['GET'])
def churn_count():
    try:
        cursor = get_db_cursor()
        cursor.execute("SELECT COUNT(*) as churned FROM customers WHERE prediction = 1")
        churned = cursor.fetchone()['churned']
        cursor.execute("SELECT COUNT(*) as total FROM customers")
        total = cursor.fetchone()['total']
        cursor.close()
        return jsonify({'churned': churned, 'total': total})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/customers/churn_summary', methods=['GET'])
def churn_summary():
    try:
        cursor = get_db_cursor()
        cursor.execute("SELECT prediction, COUNT(*) as count FROM customers GROUP BY prediction")
        summary = cursor.fetchall()
        cursor.close()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/customers/predicted', methods=['GET'])
def get_predicted_customers():
    try:
        threshold = float(request.args.get('threshold', 50)) / 100.0
        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM customers WHERE Churn_Probability >= %s", (threshold,))
        customers = cursor.fetchall()
        cursor.close()
        return jsonify(customers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 