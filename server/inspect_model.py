import joblib

# Load your .joblib file
model = joblib.load('ml_models/primary_bot_detector.joblib')

# Print the object
print(type(model))
print(model)