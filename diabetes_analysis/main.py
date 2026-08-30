# -------------------------------------
# Diabetes Prediction using Linear Regression and Tkinter GUI
# -------------------------------------

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import tkinter as tk
from tkinter import messagebox

# Load dataset
data = load_diabetes()
df = pd.DataFrame(data.data, columns=data.feature_names)
df["target"] = data.target

# Prepare data for training
X = df.drop("target", axis=1)
y = df["target"]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate the model
mse = mean_squared_error(y_test, model.predict(X_test))
r2 = r2_score(y_test, model.predict(X_test))
print(f"✅ Model trained successfully.")
print(f"R² Score: {r2:.2f}")
print(f"Mean Squared Error: {mse:.2f}")

# -------------------------------------
# Create a Tkinter GUI for user input
# -------------------------------------
root = tk.Tk()
root.title("Diabetes Prediction System")
root.geometry("450x600")
root.configure(bg="#282a36")

# Title Label
title_label = tk.Label(root, text="🔮 Diabetes Prediction System", bg="#282a36", fg="white", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

entries = {}
for feature in data.feature_names:
    frame = tk.Frame(root, bg="#282a36")
    frame.pack(pady=3)
    tk.Label(frame, text=feature, width=15, anchor="w", bg="#282a36", fg="white").pack(side="left", padx=5)
    entry = tk.Entry(frame, width=20)
    entry.pack(side="left")
    entries[feature] = entry

# Prediction function
def predict():
    try:
        user_input = [float(entries[f].get()) for f in data.feature_names]
        pred = model.predict([user_input])[0]
        messagebox.showinfo("Prediction Result", f"Predicted disease progression value: {pred:.2f}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values!")

# Prediction button
btn = tk.Button(root, text="🔍 Predict Now", command=predict, bg="#50fa7b", fg="black", font=("Arial", 12, "bold"))
btn.pack(pady=20)

# Model accuracy display
lbl_score = tk.Label(root, text=f"Model R² Score: {r2:.2f}", bg="#282a36", fg="#8be9fd", font=("Arial", 12))
lbl_score.pack(pady=10)
root.mainloop()