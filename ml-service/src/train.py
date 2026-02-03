# Model training

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Sentinel Intelligence: Model Definition
class PhishingSentinelModel(nn.Module):
    def __init__(self, input_size):
        super(PhishingSentinelModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        return self.network(x)

def train_model(csv_path="datasets/Dataset.csv"):
    print(f"[Sentinel] Loading Dataset: {csv_path}...")
    
    # 1. Load and Preprocess Data
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Please ensure the dataset is in the ml-service folder.")
        return

    df = pd.read_csv(csv_path)
    
    # Separate features and target (Target is 'Type')
    X = df.drop('Type', axis=1).values
    y = df['Type'].values.reshape(-1, 1)
    
    # 2. Feature Scaling (Crucial for Neural Networks)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Save the scaler to use during real-time inference
    model_dir = "models"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))

    # 3. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    # Convert to Tensors
    train_data = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
    test_data = TensorDataset(torch.FloatTensor(X_test), torch.FloatTensor(y_test))
    
    train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_data, batch_size=64, shuffle=False)

    # 4. Initialize Model (41 features)
    input_size = X.shape[1] 
    model = PhishingSentinelModel(input_size=input_size)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # 5. Training Loop
    epochs = 30
    print(f"[Sentinel] Starting Training on {len(X_train)} samples...")
    
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
            
        if (epoch + 1) % 5 == 0:
            # Simple Validation
            model.eval()
            with torch.no_grad():
                correct = 0
                total = 0
                for tx, ty in test_loader:
                    t_out = model(tx)
                    predicted = (t_out > 0.5).float()
                    total += ty.size(0)
                    correct += (predicted == ty).sum().item()
                accuracy = 100 * correct / total
                print(f"Epoch [{epoch+1}/{epochs}], Loss: {epoch_loss/len(train_loader):.4f}, Val Acc: {accuracy:.2f}%")
            
    # 6. Save the Model
    model_path = os.path.join(model_dir, "sentinel_v1.pth")
    torch.save(model.state_dict(), model_path)
    print(f"[Sentinel] Model and Scaler saved successfully.")

if __name__ == "__main__":
    train_model()