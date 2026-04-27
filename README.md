# 📊 Philippine Agri Farmgate and Retail Price Analysis

## ⚙️ Backend API System (Data Processing & Analytics Layer Only)
An automated data pipeline and analytical API designed to examine the relationship between farmgate prices and retail prices for key agricultural commodities in the Philippines (2021–2025).

---

## 📌 Project Overview
This project addresses the transparency gap in the Philippine agricultural supply chain. By integrating datasets from the Philippine Statistics Authority (PSA), the system provides real-time analysis of marketing margins and applies econometric tests to determine price transmission efficiency.

---

## 🎯 Key Objectives
- **Standardization**: Transform disparate CSV/Excel datasets into a unified **long-format time series**
- **Margin Analysis**: Calculate the **Marketing Margin** and **Farmer's Share** for core commodities (Banana, Mango, Pineapple, Coconut, Cassava, Ube, Palay, Corn)
- **Predictive Analytics**: Utilize **Granger Causality** to determine if farmgate price changes predict retail price movements

---

## 🛠️ Technical Stack
- **Language**: Python 3.10+
- **Framework**: FastAPI (Backend API)
- **Data Processing**: Pandas, NumPy
- **Statistics**: Statsmodels (Granger Causality, VAR)
- **Documentation**: Swagger UI / OpenAPI

---

## 📂 Project Structure
- **standardize_data.py** – Script to clean and merge raw PSA datasets  
- **main.py** – FastAPI backend with analysis logic  
- **Standardized_Farmgate_Retail_Final_Data.csv** – Final cleaned dataset  
- **README.md** – Project documentation

---

## 🚀 Getting Started
## 1. Installation
Clone the repository and install dependencies:
```bash
pip install fastapi uvicorn pandas numpy statsmodels
```
## 2. Data Standardization
Process raw datasets before running the API:
```bash
python standardize_data.py
```
## 3. Run the API
```bash
uvicorn main:app --reload
```
then open: 
http://127.0.0.1:8000/docs

---
## 📊 API Endpoints & Features

### 1. Marketing Margin Analysis
**Endpoint:** `/analysis/margin/{commodity}`  

- Computes price spread and farmer share  

**Formulas:**
- `Margin = Retail - Farmgate`  
- `Farmer's Share = (Farmgate / Retail) × 100`  

---

### 2. Granger Causality Test
**Endpoint:** `/analysis/causality/{commodity}`  

- Tests if farmgate prices predict retail prices  

**Interpretation:**
- `p-value < 0.05` → Significant relationship  
- Indicates responsive or delayed price transmission  

---

### 3. Time-Series Trends
**Endpoint:** `/analysis/trends`  

- Aggregates data monthly or yearly  
- Identifies trends, inflation, and seasonal patterns  

---

## 📈 Economic Significance

This system helps identify:

- **Market Inefficiency** → Large margins indicate high intermediary costs  
- **Price Rigidity** → Retail prices remain high despite falling farmgate prices  
- **Food Security Risks** → Volatility in staple crops like rice (palay) and corn  

## 📊 Dataset

- **Source**: Philippine Statistics Authority (PSA)  
- **Coverage**: 2021–2025  
- **Commodities**: Rice, Corn, Coconut, Cassava, Banana, Pineapple, Mango, Ube  

---

## 👨‍💻 Contributors
- **ARONG** – 
- **LOPEZ** - 
- **LOSORATA** – Data Analyst & Backend Developer 
