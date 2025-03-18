from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import logging
import os

app = Flask(__name__)

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)

# Load course data
try:
    data = pd.read_csv('models/courses.csv')
    if data.empty:
        print("Error: courses.csv is empty or incorrectly formatted. Please check.")
        exit()
except FileNotFoundError:
    print("Error: courses.csv file not found. Please place it in the models folder.")
    exit()

# Course categories mapping
course_categories = {
    "machine learning": 1,
    "python": 2,
    "data science": 1,
    "web development": 3,
    "cybersecurity": 4,
    "digital marketing": 5
}

# Models for prediction
def predict_completion(past_performance):
    X = data[['Past_Performance']].values
    y = data['Completion_Probability'].values
    model = LinearRegression()
    model.fit(X, y)
    
    prediction = model.predict([[past_performance]])
    
    # Cap probability between 0 and 1 to avoid invalid responses
    completion_probability = max(0, min(prediction[0], 1))
    return f"The likelihood of completing the course is {round(completion_probability * 100, 2)}%"

def classify_query(query):
    query_data = ['course details', 'schedule', 'prerequisites', 'fees', 'duration', 'completion rate']
    labels = [0, 1, 2, 3, 4, 5]
    
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(query_data)
    
    model_lr = LogisticRegression()
    model_lr.fit(X, labels)
    
    query_vec = vectorizer.transform([query])
    prediction = model_lr.predict(query_vec)
    
    query_types = ['Course Details', 'Schedule', 'Prerequisites', 'Fees', 'Duration', 'Completion Rate']
    
    if prediction[0] < len(query_types):
        return query_types[prediction[0]]
    else:
        return "Sorry, I couldn't classify your query."

def recommend_course(student_performance, interests):
    interests = interests.lower().strip()
    
    # Handle unknown interest early
    if interests == "unknown":
        return "Please specify a valid interest like machine learning, python, cybersecurity, etc."
    
    # Check for interest match in the course list
    filtered_data = data[
        (data['Interest_Level'] >= 6) &  # Only consider courses with high interest
        (data['Past_Performance'] <= student_performance + 10) &  # Performance threshold
        (data['Course'].str.lower().str.contains(interests))  # Match interest
    ]
    
    # If no matching course found, give a fallback message
    if len(filtered_data) == 0:
        return "Sorry, no courses found related to your interest."

    # Select the most relevant course based on performance
    recommended_course = filtered_data.iloc[0]['Course_Recommendation']
    return f"We recommend the course: {recommended_course}"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input'].lower()
    logging.info(f"User Input: {user_input}")

    # Check for recommendation-related query
    if any(keyword in user_input for keyword in ["recommend", "suggest", "course"]):
        interest = "unknown"
        performance = 70  # Default performance if not provided

        # Check if the user provided interest explicitly
        if "cybersecurity" in user_input:
            interest = "cybersecurity"
        elif "machine learning" in user_input:
            interest = "machine learning"
        elif "python" in user_input:
            interest = "python"
        elif "data science" in user_input:
            interest = "data science"
        elif "web development" in user_input:
            interest = "web development"
        elif "digital marketing" in user_input:
            interest = "digital marketing"

        # Extract performance if mentioned in the query
        performance_values = [int(s) for s in user_input.split() if s.isdigit()]
        performance = performance_values[0] if performance_values else 70

        # Call recommendation function
        response = recommend_course(performance, interest)

    # Check for completion probability query
    elif "completion" in user_input:
        performance_values = [float(s) for s in user_input.split() if s.replace('.', '', 1).isdigit()]
        performance = performance_values[0] if performance_values else 70  # Default to 70 if not mentioned
        response = predict_completion(performance)

    # Check for classification of query
    elif any(keyword in user_input for keyword in ["details", "schedule", "fees"]):
        response = classify_query(user_input)

    # If no matching query
    else:
        response = "I am sorry! I don't understand your query."

    return jsonify({'response': response})


if __name__ == '__main__':
    app.run(debug=True)
