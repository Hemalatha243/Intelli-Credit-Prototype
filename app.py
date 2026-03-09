
import os

# Create directory
os.makedirs('/mnt/user-data/uploads/intelli-credit', exist_ok=True)

# Save app.py
with open('/mnt/user-data/uploads/intelli-credit/app.py', 'w') as f:
    f.write(app_code)

print("✅ Created app.py")

# Create requirements.txt
requirements = """streamlit==1.28.0
pandas==2.0.3
numpy==1.24.3
plotly==5.17.0
scikit-learn==1.3.0
PyPDF2==3.0.1
openpyxl==3.1.2
python-docx==0.8.11
"""

with open('/mnt/user-data/uploads/intelli-credit/requirements.txt', 'w') as f:
    f.write(requirements)

print("✅ Created requirements.txt")

# Create README.md
readme = """# 🏦 Intelli-Credit: AI-Powered Credit Decisioning Engine

**Hackathon Prototype for Corporate Credit Appraisal**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](YOUR_STREAMLIT_URL_HERE)

## 🎯 Problem Statement
Automated AI-powered Credit Decisioning Engine for Indian corporate lending that handles:
- Multi-format data ingestion (GST, ITR, Bank Statements, Annual Reports)
- Web-scale secondary research (News, Litigation, Regulatory)
- Explainable AI scoring (Five Cs of Credit)
- Automated CAM (Credit Appraisal Memo) generation

## 🚀 Features

### 1. Data Ingestor (Pillar 1)
- 📄 PDF parsing for Annual Reports & Legal notices
- 📊 GST Reconciliation (GSTR-2A vs GSTR-3B)
- 🔍 Circular Trading Detection
- 🏦 Bank Statement Analysis
- ☁️ Databricks Integration ready

### 2. Research Agent (Pillar 2)
- 📰 Automated News Monitoring & Sentiment Analysis
- ⚖️ Litigation tracking (NCLT, DRT, High Courts)
- 🏭 Site Visit Portal for primary due diligence
- 📊 Sector Analysis & Regulatory updates

### 3. Recommendation Engine (Pillar 3)
- 🧠 Five Cs of Credit Scoring (Character, Capacity, Capital, Collateral, Conditions)
- 🔍 Explainable AI (XAI) with SHAP-like feature importance
- 📄 Automated CAM Generation (Word/PDF)
- ✅ Approval/Rejection with conditions

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **Data**: Pandas, NumPy
- **ML**: Scikit-learn
- **Viz**: Plotly
- **Documents**: PyPDF2, python-docx

## 🎮 Demo Mode
The app includes realistic mock data generators for:
- Low Risk profiles (Strong financials, no litigation)
- Medium Risk profiles (Average metrics, minor issues)
- High Risk profiles (Weak financials, litigation, GST issues)

## 🏛️ Indian Context Features
- CIN (Corporate Identification Number) validation
- GSTIN format handling
- GSTR-2A vs 3B reconciliation
- MCA21 integration placeholders
- Indian banking sector risk weights

## 🚀 Deployment

### Streamlit Cloud (Recommended)
1. Fork this repo to your GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Deploy!

### Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Repository Structure
```
intelli-credit/
├── app.py              # Main application (single file)
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## 🏆 Hackathon Evaluation Criteria Covered
- ✅ **Extraction Accuracy**: PDF/Excel parsing with confidence scores
- ✅ **Research Depth**: News, litigation, sector analysis
- ✅ **Explainability**: XAI with factor breakdowns
- ✅ **Indian Context**: GST, CIN, MCA, CIBIL placeholders

## 📝 License
MIT License - Hackathon Project

## 👥 Team
Built for Intelli-Credit Hackathon Challenge 2024
"""

with open('/mnt/user-data/uploads/intelli-credit/README.md', 'w') as f:
    f.write(readme)

print("✅ Created README.md")

# List files
print("\\n📂 Repository structure:")
for f in os.listdir('/mnt/user-data/uploads/intelli-credit'):
    size = os.path.getsize(f'/mnt/user-data/uploads/intelli-credit/{f}')
    print(f"  ├── {f} ({size:,} bytes)")
