
# Save this as app.py - Complete Intelli-Credit Engine
"""
Intelli-Credit: AI-Powered Credit Decisioning Engine
Hackathon Prototype - Streamlit Deployment Ready
Author: AI Assistant
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import re
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import random
import hashlib
import io
from pathlib import Path

# Visualization
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ML/Analysis
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import shap

# Document processing (simulated for demo)
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# Configure Streamlit Page
st.set_page_config(
    page_title="Intelli-Credit | AI Credit Decisioning",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Indian Banking Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(30, 58, 138, 0.2);
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #3b82f6;
        transition: transform 0.2s;
    }
    
    .metric-card:hover { transform: translateY(-2px); }
    
    .risk-high { border-left-color: #dc2626; }
    .risk-medium { border-left-color: #f59e0b; }
    .risk-low { border-left-color: #10b981; }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .cam-section {
        background: #f8fafc;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .explanation-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f1f5f9;
        border-radius: 8px 8px 0 0;
        padding: 1rem 2rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        color: white !important;
    }
    
    .upload-zone {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #f8fafc;
        transition: all 0.3s;
    }
    
    .upload-zone:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    
    /* Indian Context Badges */
    .india-badge {
        background: #ff9933;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA MODELS ====================

class LoanDecision(str, Enum):
    APPROVE = "✅ APPROVE"
    REJECT = "❌ REJECT"
    REVIEW = "⚠️ MANUAL REVIEW"
    CONDITIONAL = "📋 CONDITIONAL"

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

@dataclass
class CompanyInfo:
    cin: str
    name: str
    pan: str
    gstin: List[str]
    industry: str
    incorporation_date: str
    promoters: List[str]
    address: str

@dataclass
class FinancialMetrics:
    revenue_cr: float
    growth_rate: float
    ebitda_margin: float
    debt_equity: float
    current_ratio: float
    interest_coverage: float
    avg_bank_balance_cr: float
    gst_compliance: float

@dataclass
class FiveCsScore:
    character: float
    capacity: float
    capital: float
    collateral: float
    conditions: float
    explanations: Dict[str, str]

@dataclass
class CreditRecommendation:
    decision: LoanDecision
    limit_cr: float
    tenure_months: int
    interest_rate: float
    risk_rating: str
    five_cs: FiveCsScore
    explanation: str
    confidence: float

# ==================== MOCK DATA GENERATORS ====================

class MockDataGenerator:
    """Generate realistic Indian corporate data for demo purposes"""
    
    INDUSTRIES = [
        "Textiles", "Auto Components", "Pharmaceuticals", "IT Services",
        "Food Processing", "Chemicals", "Construction", "Trading",
        "Manufacturing", "Logistics"
    ]
    
    FIRST_NAMES = ["Rajesh", "Suresh", "Amit", "Vikram", "Sanjay", "Prakash", "Manish", "Rahul"]
    LAST_NAMES = ["Sharma", "Patel", "Agarwal", "Gupta", "Mehta", "Shah", "Kumar", "Singh"]
    
    @staticmethod
    def generate_cin():
        """Generate valid format CIN (Corporate Identification Number)"""
        prefix = random.choice(["U", "L"])
        digits = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        year = random.randint(1990, 2023)
        state = random.choice(["MH", "GJ", "KA", "TN", "DL", "TG", "UP", "WB"])
        sequence = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return f"{prefix}{digits}{year}{state}{sequence}"
    
    @staticmethod
    def generate_gstin(state_code="27"):
        """Generate GSTIN format"""
        pan = ''.join([random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(5)])
        pan += ''.join([str(random.randint(0, 9)) for _ in range(4)])
        pan += random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
        entity = str(random.randint(1, 9))
        checksum = "Z" + str(random.randint(1, 9))
        return f"{state_code}{pan}{entity}{checksum}"
    
    @classmethod
    def generate_company(cls, risk_profile: str = "random"):
        """Generate complete company profile"""
        name = f"{random.choice(cls.FIRST_NAMES)} {random.choice(['Industries', 'Enterprises', 'Technologies', 'Corporation'])} Ltd"
        
        # Adjust metrics based on risk profile
        if risk_profile == "low":
            growth = random.uniform(15, 30)
            debt_equity = random.uniform(0.5, 1.2)
            gst_compliance = random.uniform(95, 100)
        elif risk_profile == "high":
            growth = random.uniform(-10, 5)
            debt_equity = random.uniform(2.5, 4.0)
            gst_compliance = random.uniform(60, 85)
        else:
            growth = random.uniform(5, 20)
            debt_equity = random.uniform(1.0, 2.5)
            gst_compliance = random.uniform(85, 98)
        
        return CompanyInfo(
            cin=cls.generate_cin(),
            name=name,
            pan="".join([random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(5)]) + \
                "".join([str(random.randint(0, 9)) for _ in range(4)]) + random.choice("A"),
            gstin=[cls.generate_gstin(), cls.generate_gstin("29")],
            industry=random.choice(cls.INDUSTRIES),
            incorporation_date=f"{random.randint(1995, 2018)}-{random.randint(1, 12):02d}-15",
            promoters=[f"{random.choice(cls.FIRST_NAMES)} {random.choice(cls.LAST_NAMES)}" for _ in range(2)],
            address=f"Plot No {random.randint(1, 500)}, Industrial Area, {random.choice(['Mumbai', 'Ahmedabad', 'Bangalore', 'Chennai', 'Delhi', 'Hyderabad'])}"
        ), FinancialMetrics(
            revenue_cr=random.uniform(50, 500),
            growth_rate=growth,
            ebitda_margin=random.uniform(8, 25),
            debt_equity=debt_equity,
            current_ratio=random.uniform(1.0, 2.5),
            interest_coverage=random.uniform(1.5, 6.0),
            avg_bank_balance_cr=random.uniform(5, 50),
            gst_compliance=gst_compliance
        )
    
    @staticmethod
    def generate_news(company_name: str, risk_profile: str):
        """Generate realistic news items"""
        positive_templates = [
            f"{company_name} secures major export order worth ₹{random.randint(50, 200)}Cr",
            f"{company_name} announces capacity expansion in {random.choice(['Gujarat', 'Maharashtra', 'Karnataka'])}",
            f"{company_name} receives 'Best SME' award from {random.choice(['FICCI', 'CII', 'Assocham'])}",
            f"Promoter of {company_name} appointed to {random.choice(['RBI advisory', 'Industry body', 'Export council'])}",
        ]
        
        negative_templates = [
            f"{company_name} faces GST scrutiny for ITC mismatch",
            f"Promoter of {company_name} named in {random.choice(['bank fraud', 'cheque bounce', 'contract dispute'])} case",
            f"{company_name} delays Q{random.randint(1, 4)} results citing audit issues",
            f"Workers strike at {company_name} factory over wage disputes",
            f"RBI cautions banks against lending to {company_name} sector",
        ]
        
        news = []
        if risk_profile in ["low", "medium"]:
            news.extend([{"title": t, "sentiment": "positive", "source": random.choice(["ET", "BS", "Mint"]), 
                         "date": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")} 
                        for t in random.sample(positive_templates, 3)])
        
        if risk_profile in ["high", "medium"]:
            news.extend([{"title": t, "sentiment": "negative", "source": random.choice(["ET", "BS", "Mint"]),
                         "date": (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")}
                        for t in random.sample(negative_templates, 2)])
        
        return news
    
    @staticmethod
    def generate_litigation(risk_profile: str):
        """Generate litigation data"""
        if risk_profile == "low":
            return []
        
        cases = []
        num_cases = 1 if risk_profile == "medium" else random.randint(2, 4)
        
        for i in range(num_cases):
            cases.append({
                "case_no": f"CS/{random.randint(100, 999)}/{random.randint(2020, 2023)}",
                "court": random.choice(["Bombay HC", "Delhi HC", "NCLT Mumbai", "DRT"]),
                "petitioner": random.choice(["Bank", "Vendor", "Revenue Dept"]),
                "amount_cr": random.uniform(1, 20),
                "status": random.choice(["Pending", "Disposed"]),
                "risk": "High" if risk_profile == "high" else "Medium"
            })
        return cases

# ==================== CORE ENGINE ====================

class CreditDecisioningEngine:
    """Main AI Engine for Credit Decisioning"""
    
    def __init__(self):
        self.risk_weights = {
            'financial': 0.30,
            'promoter': 0.25,
            'industry': 0.20,
            'behavioral': 0.15,
            'external': 0.10
        }
    
    def calculate_five_cs(self, company: CompanyInfo, financials: FinancialMetrics, 
                         news: List[Dict], litigation: List[Dict]) -> FiveCsScore:
        """Calculate Five Cs of Credit with Indian context"""
        
        # Character (Promoter integrity + Compliance)
        gst_score = financials.gst_compliance
        negative_news = sum(1 for n in news if n['sentiment'] == 'negative')
        litigation_penalty = len(litigation) * 15
        character = max(0, min(100, gst_score - (negative_news * 10) - litigation_penalty))
        
        char_exp = f"GST Compliance: {gst_score}%. "
        if negative_news > 0:
            char_exp += f"Found {negative_news} adverse news items. "
        if litigation:
            char_exp += f"Active litigation: {len(litigation)} case(s)."
        if character > 75:
            char_exp += " Overall strong promoter integrity."
        
        # Capacity (Debt servicing ability)
        if financials.interest_coverage > 3 and financials.debt_equity < 1.5:
            capacity = 85
        elif financials.interest_coverage > 1.5:
            capacity = 65
        else:
            capacity = 40
        
        cap_exp = f"Interest Coverage: {financials.interest_coverage:.2f}x. "
        cap_exp += f"D/E: {financials.debt_equity:.2f}. "
        cap_exp += "Strong debt servicing capacity." if capacity > 75 else "Adequate capacity with monitoring." if capacity > 50 else "Weak capacity - major concern."
        
        # Capital (Financial cushion)
        net_worth_indicator = financials.revenue_cr / (financials.debt_equity + 0.1)
        if net_worth_indicator > 100:
            capital = 80
        elif net_worth_indicator > 50:
            capital = 60
        else:
            capital = 40
        
        capi_exp = f"Revenue/Debt ratio indicates {'strong' if capital > 70 else 'moderate' if capital > 50 else 'weak'} net worth position."
        
        # Collateral (Security coverage - simulated)
        collateral = 70 if financials.debt_equity < 2 else 50
        coll_exp = "Adequate tangible security coverage expected based on industry norms."
        
        # Conditions (Industry + Macro)
        industry_risk = {"Textiles": 60, "Auto Components": 75, "Pharmaceuticals": 80, 
                        "IT Services": 85, "Construction": 50, "Trading": 55}
        base_conditions = industry_risk.get(company.industry, 65)
        if financials.growth_rate < 0:
            base_conditions -= 20
        conditions = max(0, min(100, base_conditions))
        
        cond_exp = f"{company.industry} sector outlook: {'Favorable' if conditions > 70 else 'Stable' if conditions > 50 else 'Challenging'}. "
        cond_exp += f"Company growth: {financials.growth_rate:.1f}%."
        
        return FiveCsScore(
            character=character,
            capacity=capacity,
            capital=capital,
            collateral=collateral,
            conditions=conditions,
            explanations={
                "Character": char_exp,
                "Capacity": cap_exp,
                "Capital": capi_exp,
                "Collateral": coll_exp,
                "Conditions": cond_exp
            }
        )
    
    def detect_circular_trading(self, gst_data: pd.DataFrame) -> Dict:
        """Detect circular trading patterns in GST data"""
        # Simulate circular trading detection
        risk_score = random.randint(0, 100)
        
        patterns = []
        if risk_score > 70:
            patterns = [
                "High value invoices to shell-like entities detected",
                "Mismatch between GSTR-1 and 3B filings (>20% variance)",
                "Common addresses found across multiple suppliers"
            ]
        elif risk_score > 40:
            patterns = [
                "Moderate variance in monthly filings",
                "New high-value suppliers added recently"
            ]
        
        return {
            "risk_score": risk_score,
            "patterns": patterns,
            "recommendation": "Deep investigation required" if risk_score > 70 else "Standard monitoring" if risk_score > 40 else "Low risk"
        }
    
    def generate_recommendation(self, company: CompanyInfo, financials: FinancialMetrics,
                               five_cs: FiveCsScore, circular_risk: Dict) -> CreditRecommendation:
        """Generate final credit recommendation with XAI explanation"""
        
        # Calculate composite score
        weights = [0.30, 0.30, 0.20, 0.10, 0.10]  # Char, Cap, Cap, Coll, Cond
        scores = [five_cs.character, five_cs.capacity, five_cs.capital, five_cs.collateral, five_cs.conditions]
        composite = np.average(scores, weights=weights)
        
        # Adjust for circular trading
        if circular_risk['risk_score'] > 70:
            composite -= 20
        
        # Decision logic with Indian banking norms
        if composite >= 75 and circular_risk['risk_score'] < 50:
            decision = LoanDecision.APPROVE
            limit = financials.revenue_cr * 0.25  # 25% of revenue
            rate = 8.5 + (100 - composite) * 0.05  # Base MCLR + spread
        elif composite >= 60:
            decision = LoanDecision.CONDITIONAL
            limit = financials.revenue_cr * 0.15
            rate = 9.5 + (100 - composite) * 0.08
        elif composite >= 45:
            decision = LoanDecision.REVIEW
            limit = financials.revenue_cr * 0.10
            rate = 11.0
        else:
            decision = LoanDecision.REJECT
            limit = 0
            rate = 0
        
        # Generate natural language explanation (XAI)
        explanation = self._generate_explanation(decision, composite, five_cs, circular_risk, financials)
        
        # Risk rating
        if composite >= 80:
            risk_rating = "AAA (Investment Grade)"
        elif composite >= 70:
            risk_rating = "AA (Strong)"
        elif composite >= 60:
            risk_rating = "A (Adequate)"
        elif composite >= 50:
            risk_rating = "BBB (Moderate Risk)"
        elif composite >= 40:
            risk_rating = "BB (Speculative)"
        else:
            risk_rating = "B (High Risk)"
        
        return CreditRecommendation(
            decision=decision,
            limit_cr=round(limit, 2),
            tenure_months=36 if decision != LoanDecision.REJECT else 0,
            interest_rate=round(rate, 2),
            risk_rating=risk_rating,
            five_cs=five_cs,
            explanation=explanation,
            confidence=round(min(95, composite + 10), 1)
        )
    
    def _generate_explanation(self, decision: LoanDecision, score: float, 
                             five_cs: FiveCsScore, circular: Dict, fin: FinancialMetrics) -> str:
        """Generate human-readable explanation (SHAP-like)"""
        
        parts = []
        
        # Decision summary
        if decision == LoanDecision.REJECT:
            parts.append(f"❌ **REJECTION RECOMMENDED** (Composite Score: {score:.1f}/100)")
            parts.append("\n**Primary Reasons:**")
            if five_cs.character < 60:
                parts.append(f"• Poor Character score ({five_cs.character}/100) due to compliance issues or litigation")
            if five_cs.capacity < 50:
                parts.append(f"• Inadequate debt servicing capacity ({five_cs.capacity}/100)")
            if circular['risk_score'] > 60:
                parts.append(f"• High circular trading risk detected ({circular['risk_score']}/100)")
        
        elif decision == LoanDecision.CONDITIONAL:
            parts.append(f"📋 **CONDITIONAL APPROVAL** (Composite Score: {score:.1f}/100)")
            parts.append("\n**Conditions Precedent:**")
            parts.append("• Personal guarantee of promoters")
            parts.append("• Quarterly monitoring of GST compliance")
            if five_cs.collateral < 60:
                parts.append("• Additional collateral security")
        
        else:
            parts.append(f"✅ **APPROVAL RECOMMENDED** (Composite Score: {score:.1f}/100)")
            parts.append("\n**Key Strengths:**")
            parts.append(f"• Strong {fin.gst_compliance}% GST compliance track record")
            parts.append(f"• Healthy interest coverage of {fin.interest_coverage:.2f}x")
            if fin.growth_rate > 10:
                parts.append(f"• Robust revenue growth of {fin.growth_rate:.1f}%")
        
        # Feature importance explanation
        parts.append("\n**Score Breakdown (Feature Importance):**")
        parts.append(f"• Character (30%): {five_cs.character}/100 - {five_cs.explanations['Character']}")
        parts.append(f"• Capacity (30%): {five_cs.capacity}/100 - {five_cs.explanations['Capacity']}")
        parts.append(f"• Capital (20%): {five_cs.capital}/100")
        parts.append(f"• Conditions (10%): {five_cs.conditions}/100")
        
        return "\n".join(parts)

# ==================== DOCUMENT PARSER ====================

class DocumentParser:
    """Handle PDF, Excel, Image parsing"""
    
    def __init__(self):
        self.supported_types = ['pdf', 'xlsx', 'xls', 'csv', 'png', 'jpg']
    
    def parse_file(self, file) -> Dict:
        """Parse uploaded file and extract structured data"""
        file_type = file.name.split('.')[-1].lower()
        
        if file_type == 'pdf':
            return self._parse_pdf(file)
        elif file_type in ['xlsx', 'xls']:
            return self._parse_excel(file)
        elif file_type == 'csv':
            return self._parse_csv(file)
        else:
            return {"error": "Unsupported file type", "type": file_type}
    
    def _parse_pdf(self, file) -> Dict:
        """Extract text and tables from PDF"""
        try:
            if PDF_SUPPORT:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                # Extract key financial data using regex
                revenue = self._extract_amount(text, [r'Revenue[\s:]+₹?([\d,]+) Cr', r'Turnover[\s:]+₹?([\d,]+) Cr'])
                
                return {
                    "type": "PDF",
                    "pages": len(pdf_reader.pages),
                    "text_sample": text[:500] + "...",
                    "extracted_revenue": revenue,
                    "status": "Parsed successfully"
                }
            else:
                return {
                    "type": "PDF",
                    "status": "PyPDF2 not installed (demo mode)",
                    "extracted_revenue": f"₹{random.randint(50, 500)} Cr (simulated)"
                }
        except Exception as e:
            return {"error": str(e), "type": "PDF"}
    
    def _parse_excel(self, file) -> Dict:
        """Parse Excel files (GST returns, Bank statements)"""
        try:
            df = pd.read_excel(file)
            return {
                "type": "Excel",
                "rows": len(df),
                "columns": list(df.columns),
                "sample": df.head(3).to_dict(),
                "gst_summary": {
                    "total_taxable_value": f"₹{random.randint(10, 100)}Cr",
                    "igst_paid": f"₹{random.randint(1, 10)}Cr",
                    "compliance_score": f"{random.randint(85, 100)}%"
                }
            }
        except Exception as e:
            return {"error": str(e), "type": "Excel"}
    
    def _parse_csv(self, file) -> Dict:
        """Parse CSV bank statements"""
        try:
            df = pd.read_csv(file)
            return {
                "type": "CSV",
                "transactions": len(df),
                "avg_balance": f"₹{random.randint(5, 50)}Cr",
                "status": "Bank statement analyzed"
            }
        except Exception as e:
            return {"error": str(e), "type": "CSV"}
    
    def _extract_amount(self, text: str, patterns: List[str]) -> Optional[str]:
        """Extract monetary amounts using regex"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"₹{match.group(1)} Cr"
        return None

# ==================== UI COMPONENTS ====================

def render_header():
    """Render application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🏦 Intelli-Credit</h1>
        <h3>AI-Powered Corporate Credit Decisioning Engine</h3>
        <p style="opacity: 0.9; margin-top: 1rem;">
            <span class="india-badge">INDIA SPECIFIC</span> 
            Next-Gen Credit Appraisal | GST Analytics | Litigation Monitoring | XAI Explainability
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/bank-building.png", width=80)
        st.title("Navigation")
        
        page = st.radio("", [
            "📊 Dashboard",
            "📁 Data Ingestion", 
            "🔍 Research Agent",
            "🧠 Credit Analysis",
            "📄 CAM Generator",
            "⚙️ Settings"
        ])
        
        st.divider()
        
        # Demo mode selector
        st.subheader("🎮 Demo Mode")
        risk_profile = st.select_slider(
            "Select Risk Profile",
            options=["Low Risk", "Medium Risk", "High Risk"],
            value="Medium Risk"
        )
        
        st.divider()
        st.caption("© 2024 Intelli-Credit v1.0")
        
        return page, risk_profile.lower().replace(" ", "_")

def render_dashboard(engine: CreditDecisioningEngine, mock_gen: MockDataGenerator):
    """Render main dashboard"""
    st.subheader("📊 Portfolio Overview")
    
    cols = st.columns(4)
    metrics = [
        ("Total Applications", "156", "+12%", "normal"),
        ("Avg Processing Time", "4.2 days", "-65%", "inverse"),
        ("Approval Rate", "68%", "+5%", "normal"),
        ("Risk Detected", "23", "-8%", "inverse")
    ]
    
    for col, (label, value, delta, delta_type) in zip(cols, metrics):
        with col:
            st.metric(label, value, delta, delta_color="normal" if delta_type == "normal" else "inverse")
    
    # Recent applications table
    st.subheader("Recent Applications")
    
    recent_data = []
    for i in range(5):
        company, financials = mock_gen.generate_company(random.choice(["low", "medium", "high"]))
        recent_data.append({
            "Application ID": f"APP-{2024}{random.randint(1000, 9999)}",
            "Company": company.name,
            "Industry": company.industry,
            "Amount Requested": f"₹{random.randint(10, 100)}Cr",
            "Status": random.choice(["Approved", "Under Review", "Rejected", "Conditional"]),
            "Risk Score": f"{random.randint(40, 95)}/100",
            "Last Updated": (datetime.now() - timedelta(hours=random.randint(1, 48))).strftime("%H:%M ago")
        })
    
    df_recent = pd.DataFrame(recent_data)
    
    # Color code status
    def color_status(val):
        if val == "Approved":
            return 'background-color: #dcfce7; color: #166534'
        elif val == "Rejected":
            return 'background-color: #fee2e2; color: #991b1b'
        elif val == "Conditional":
            return 'background-color: #fef3c7; color: #92400e'
        return 'background-color: #dbeafe; color: #1e40af'
    
    st.dataframe(df_recent.style.applymap(color_status, subset=['Status']), 
                use_container_width=True, hide_index=True)

def render_data_ingestion(engine: CreditDecisioningEngine, mock_gen: MockDataGenerator, risk_profile: str):
    """Render data upload and parsing section"""
    st.subheader("📁 Multi-Format Data Ingestion")
    
    tabs = st.tabs(["📄 Documents", "📊 GST/ITR", "🏦 Bank Statements", "☁️ Databricks"])
    
    parser = DocumentParser()
    
    with tabs[0]:
        st.markdown("#### Upload Annual Reports, Legal Notices, Sanction Letters")
        
        uploaded_files = st.file_uploader(
            "Drop PDF files here",
            type=['pdf'],
            accept_multiple_files=True,
            key="doc_upload"
        )
        
        if uploaded_files:
            for file in uploaded_files:
                with st.expander(f"📄 {file.name}"):
                    result = parser.parse_file(file)
                    st.json(result)
                    
                    # Show extraction confidence
                    st.progress(random.randint(75, 98), text="Extraction Confidence")
    
    with tabs[1]:
        st.markdown("#### GST Returns & ITR Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**GSTR-2A vs GSTR-3B Reconciliation**")
            
            # Mock GST data
            months = pd.date_range('2023-04-01', periods=12, freq='M')
            gstr_3b = [random.randint(45, 55) for _ in range(12)]
            gstr_2a = [x + random.randint(-5, 8) for x in gstr_3b]
            
            df_gst = pd.DataFrame({
                'Month': months.strftime('%b %Y'),
                'GSTR-3B (Output)': gstr_3b,
                'GSTR-2A (Input)': gstr_2a,
                'Variance': [abs(a-b)/b*100 for a,b in zip(gstr_3b, gstr_2a)]
            })
            
            st.dataframe(df_gst, use_container_width=True)
            
            # Circular trading detection
            circular_result = engine.detect_circular_trading(df_gst)
            
            if circular_result['risk_score'] > 50:
                st.error(f"⚠️ Circular Trading Risk: {circular_result['risk_score']}/100")
                for pattern in circular_result['patterns']:
                    st.write(f"• {pattern}")
            else:
                st.success(f"✅ Low Circular Trading Risk: {circular_result['risk_score']}/100")
        
        with col2:
            st.info("**GST Compliance Trend**")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_gst['Month'], y=df_gst['GSTR-3B (Output)'], 
                                    name='GSTR-3B', line=dict(color='#3b82f6')))
            fig.add_trace(go.Scatter(x=df_gst['Month'], y=df_gst['GSTR-2A (Input)'], 
                                    name='GSTR-2A', line=dict(color='#10b981')))
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:
        st.markdown("#### Bank Statement Analysis")
        
        uploaded_bank = st.file_uploader("Upload Bank Statement (CSV/Excel)", type=['csv', 'xlsx'])
        
        if uploaded_bank:
            result = parser.parse_file(uploaded_bank)
            st.success(f"Parsed {result.get('transactions', 'N/A')} transactions")
        else:
            # Demo bank analysis
            st.info("**Demo: Bank Statement Analytics**")
            
            # Generate synthetic bank data
            dates = pd.date_range('2023-04-01', '2024-03-31', freq='D')
            closing_balance = [random.randint(800, 1200) * 100000 for _ in dates]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=[x/10000000 for x in closing_balance], 
                                    fill='tozeroy', name='Closing Balance (Cr)'))
            fig.update_layout(title="Daily Closing Balance Trend", height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # EMI bounce detection
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Monthly Balance", "₹8.5Cr")
            col2.metric("EMI Bounces (12M)", "0", delta="Good")
            col3.metric("Cheque Returns", "2", delta="Watch")
    
    with tabs[3]:
        st.markdown("#### Databricks Integration")
        st.info("Connect to Delta Lake for historical data")
        
        st.code("""
# Example: Spark SQL Query
SELECT 
    company_cin,
    avg(monthly_revenue) as avg_revenue,
    count(distinct gstin) as gstin_count,
    max(default_flag) as ever_defaulted
FROM credit_db.gst_transactions
WHERE fy = 2023
GROUP BY company_cin
        """)
        
        if st.button("🔄 Sync from Databricks"):
            with st.spinner("Connecting to Delta Lake..."):
                import time
                time.sleep(2)
                st.success("✅ Synced 15 data sources")

def render_research_agent(mock_gen: MockDataGenerator, company: CompanyInfo, risk_profile: str):
    """Render secondary research and due diligence"""
    st.subheader("🔍 Digital Credit Manager - Research Agent")
    
    tabs = st.tabs(["📰 News Intelligence", "⚖️ Litigation Check", "🏭 Site Visit", "📊 Sector Analysis"])
    
    news = mock_gen.generate_news(company.name, risk_profile)
    litigation = mock_gen.generate_litigation(risk_profile)
    
    with tabs[0]:
        st.markdown("#### Automated News Monitoring")
        
        # News sentiment gauge
        positive = sum(1 for n in news if n['sentiment'] == 'positive')
        negative = sum(1 for n in news if n['sentiment'] == 'negative')
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=(positive / (positive + negative)) * 100 if (positive + negative) > 0 else 50,
                title={'text': "Sentiment Score"},
                gauge={'axis': {'range': [0, 100]},
                       'bar': {'color': "#10b981" if positive > negative else "#ef4444"},
                       'steps': [
                           {'range': [0, 40], 'color': "#fee2e2"},
                           {'range': [40, 70], 'color': "#fef3c7"},
                           {'range': [70, 100], 'color': "#dcfce7"}]}
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            for item in news:
                color = "🟢" if item['sentiment'] == 'positive' else "🔴"
                with st.container():
                    st.markdown(f"{color} **{item['title']}**")
                    st.caption(f"{item['source']} | {item['date']}")
                    st.divider()
    
    with tabs[1]:
        st.markdown("#### Litigation & Legal Database")
        
        if litigation:
            st.warning(f"⚠️ Found {len(litigation)} active litigation case(s)")
            
            for case in litigation:
                with st.expander(f"📁 Case: {case['case_no']}"):
                    col1, col2 = st.columns(2)
                    col1.write(f"**Court:** {case['court']}")
                    col1.write(f"**Petitioner:** {case['petitioner']}")
                    col2.write(f"**Amount:** ₹{case['amount_cr']:.2f}Cr")
                    col2.write(f"**Status:** {case['status']}")
                    
                    if case['risk'] == "High":
                        st.error("🔴 High Risk: Financial fraud allegations")
        else:
            st.success("✅ No significant litigation found")
            st.info("Searched: Supreme Court, High Courts, NCLT, DRT, NCLAT")
    
    with tabs[2]:
        st.markdown("#### Primary Due Diligence - Site Visit Portal")
        
        with st.form("site_visit_form"):
            st.write("**Factory/Management Visit Observations**")
            
            visit_date = st.date_input("Visit Date", datetime.now())
            capacity_util = st.slider("Capacity Utilization %", 0, 100, 75)
            inventory_status = st.selectbox("Inventory Levels", ["Normal", "High", "Low", "Critical"])
            labor_condition = st.selectbox("Labor Conditions", ["Good", "Satisfactory", "Poor"])
            
            observations = st.text_area("Key Observations", 
                placeholder="e.g., Factory operating at 40% capacity, outdated machinery visible...")
            
            red_flags = st.multiselect("Red Flags Observed", [
                "Underutilized capacity", "Labor unrest", "Environmental violations",
                "Stock discrepancy", "Management unavailable"
            ])
            
            submitted = st.form_submit_button("📝 Submit Observations")
            
            if submitted:
                st.success("Observations recorded! AI will adjust risk score.")
                
                # Show impact
                if capacity_util < 50 or "Underutilized capacity" in red_flags:
                    st.error("⚠️ Risk Score Impact: -15 points (Capacity concern)")
                if labor_condition == "Poor":
                    st.error("⚠️ Risk Score Impact: -10 points (Labor issues)")
    
    with tabs[3]:
        st.markdown(f"#### {company.industry} Sector Outlook")
        
        # Sector metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Industry Growth", f"{random.randint(5, 15)}%", "YoY")
        col2.metric("Credit Growth", f"{random.randint(8, 20)}%", "Industry avg")
        col3.metric("NPA Rate", f"{random.uniform(2, 8):.1f}%", "3-year avg")
        
        # Regulatory updates
        st.info("**Recent Regulatory Changes**")
        st.write("• RBI increases risk weight on unsecured lending to 125%")
        st.write("• New GST e-invoicing mandate for >₹5Cr turnover effective Jan 2024")
        st.write(f"• {company.industry} sector classified as 'Priority Sector' for FY24")

def render_credit_analysis(engine: CreditDecisioningEngine, mock_gen: MockDataGenerator, 
                          risk_profile: str, company: CompanyInfo, financials: FinancialMetrics):
    """Render the credit scoring and recommendation"""
    st.subheader("🧠 AI Credit Analysis & Scoring")
    
    # Get supporting data
    news = mock_gen.generate_news(company.name, risk_profile)
    litigation = mock_gen.generate_litigation(risk_profile)
    
    # Calculate scores
    five_cs = engine.calculate_five_cs(company, financials, news, litigation)
    circular_risk = engine.detect_circular_trading(pd.DataFrame())
    recommendation = engine.generate_recommendation(company, financials, five_cs, circular_risk)
    
    # Layout
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        # Five Cs Radar Chart
        st.markdown("#### Five Cs of Credit Analysis")
        
        categories = ['Character', 'Capacity', 'Capital', 'Collateral', 'Conditions']
        values = [five_cs.character, five_cs.capacity, five_cs.capital, 
                 five_cs.collateral, five_cs.conditions]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # Complete the loop
            theta=categories + [categories[0]],
            fill='toself',
            name='Score',
            fillcolor='rgba(59, 130, 246, 0.3)',
            line=dict(color='#3b82f6', width=2)
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed explanations
        st.markdown("#### Explainable AI (XAI) - Factor Analysis")
        for factor, explanation in five_cs.explanations.items():
            with st.expander(f"📊 {factor} Score: {getattr(five_cs, factor.lower())}/100"):
                st.write(explanation)
    
    with col_side:
        # Decision Card
        decision_color = {
            LoanDecision.APPROVE: "#10b981",
            LoanDecision.REJECT: "#ef4444",
            LoanDecision.REVIEW: "#f59e0b",
            LoanDecision.CONDITIONAL: "#8b5cf6"
        }
        
        st.markdown(f"""
        <div style="background: {decision_color[recommendation.decision]}; 
                    color: white; padding: 1.5rem; border-radius: 12px; text-align: center;">
            <h2 style="margin: 0; font-size: 1.5rem;">{recommendation.decision}</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Confidence: {recommendation.confidence}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Key metrics
        if recommendation.decision != LoanDecision.REJECT:
            st.metric("Recommended Limit", f"₹{recommendation.limit_cr}Cr")
            st.metric("Interest Rate", f"{recommendation.interest_rate}%")
            st.metric("Tenure", f"{recommendation.tenure_months} months")
        
        st.metric("Risk Rating", recommendation.risk_rating)
        
        # SHAP-style explanation
        st.divider()
        st.markdown("**Top Risk Drivers**")
        
        # Simulate feature importance
        features = [
            ("GST Compliance", five_cs.character * 0.3),
            ("Interest Coverage", five_cs.capacity * 0.3),
            ("D/E Ratio", (100 - financials.debt_equity * 20) * 0.2),
            ("Industry Outlook", five_cs.conditions * 0.1),
            ("Litigation Risk", max(0, 100 - len(litigation)*25) * 0.1)
        ]
        
        for feat, impact in sorted(features, key=lambda x: x[1], reverse=True):
            st.progress(int(impact), text=f"{feat}: {impact:.0f}/100")
    
    # Detailed explanation
    st.markdown("#### Detailed Recommendation Rationale")
    st.markdown(f"<div class='explanation-box'>{recommendation.explanation.replace(chr(10), '<br>')}</div>", 
                unsafe_allow_html=True)

def render_cam_generator(recommendation: CreditRecommendation, company: CompanyInfo, 
                        financials: FinancialMetrics):
    """Render Credit Appraisal Memo generator"""
    st.subheader("📄 Credit Appraisal Memo (CAM) Generator")
    
    cam_tabs = st.tabs(["📋 CAM Preview", "📊 Financial Summary", "🔍 Risk Assessment", "📥 Download"])
    
    with cam_tabs[0]:
        st.markdown("### CREDIT APPRAISAL MEMO")
        st.caption(f"Generated: {datetime.now().strftime('%d-%b-%Y %H:%M')} | Reference: CAM/{company.cin[:6]}/2024")
        
        # Executive Summary
        st.markdown("#### 1. EXECUTIVE SUMMARY")
        st.info(f"""
        **Borrower:** {company.name}  
        **CIN:** {company.cin}  
        **Industry:** {company.industry}  
        **Facility Requested:** Term Loan of ₹{random.randint(20, 100)}Cr  
        **Recommendation:** {recommendation.decision} (Limit: ₹{recommendation.limit_cr}Cr)
        """)
        
        # Management Analysis
        st.markdown("#### 2. MANAGEMENT & PROMOTER ANALYSIS")
        st.write(f"**Promoters:** {', '.join(company.promoters)}")
        st.write(f"**Track Record:** {random.randint(15, 30)} years in business")
        st.write(f"**Corporate Governance:** {'Satisfactory' if recommendation.five_cs.character > 60 else 'Needs Improvement'}")
        
        # Financial Analysis
        st.markdown("#### 3. FINANCIAL ANALYSIS")
        fin_data = {
            'Parameter': ['Revenue (Cr)', 'Growth %', 'EBITDA Margin %', 'D/E Ratio', 'Current Ratio', 'Interest Coverage'],
            'FY23': [f"₹{financials.revenue_cr:.1f}", f"{financials.growth_rate:.1f}%", 
                    f"{financials.ebitda_margin:.1f}%", f"{financials.debt_equity:.2f}",
                    f"{financials.current_ratio:.2f}", f"{financials.interest_coverage:.2f}x"],
            'Industry Avg': ['-', '12%', '15%', '1.5', '1.8', '3.5x']
        }
        st.table(pd.DataFrame(fin_data))
        
        # Recommendation
        st.markdown("#### 4. CREDIT RECOMMENDATION")
        st.success(f"**Decision:** {recommendation.decision}")
        st.write(f"**Sanction Amount:** ₹{recommendation.limit_cr} Crores")
        st.write(f"**Pricing:** {recommendation.interest_rate}% p.a. (Base Rate + {recommendation.interest_rate - 8:.2f}%)")
        st.write(f"**Tenure:** {recommendation.tenure_months} months")
        st.write(f"**Collateral:** Primary: Hypothecation of assets; Collateral: Immovable property")
        
        # Conditions
        st.markdown("#### 5. CONDITIONS PRECEDENT")
        st.write("• Board resolution for borrowing")
        st.write("• Personal guarantee of promoters")
        st.write("• Quarterly stock and receivables statements")
        st.write("• Annual audit by empanelled CA")
    
    with cam_tabs[1]:
        # Financial charts
        st.markdown("#### Financial Trend Analysis")
        
        years = ['FY20', 'FY21', 'FY22', 'FY23', 'FY24E']
        revenue = [financials.revenue_cr * (0.7 + i*0.1) for i in range(5)]
        
        fig = make_subplots(rows=2, cols=2, subplot_titles=('Revenue Trend', 'Profitability', 
                                                            'Leverage', 'Liquidity'))
        
        fig.add_trace(go.Bar(x=years, y=revenue, name='Revenue'), row=1, col=1)
        fig.add_trace(go.Scatter(x=years, y=[financials.ebitda_margin + random.randint(-3, 3) for _ in years], 
                                mode='lines', name='EBITDA %'), row=1, col=2)
        fig.add_trace(go.Bar(x=years, y=[financials.debt_equity + random.uniform(-0.5, 0.5) for _ in years], 
                            name='D/E'), row=2, col=1)
        fig.add_trace(go.Scatter(x=years, y=[financials.current_ratio + random.uniform(-0.3, 0.3) for _ in years], 
                                mode='lines', name='Current Ratio'), row=2, col=2)
        
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with cam_tabs[2]:
        st.markdown("#### Comprehensive Risk Assessment")
        
        risks = [
            ("Market Risk", "Medium", "Industry cyclicality affects demand"),
            ("Operational Risk", "Low", "Established manufacturing facility"),
            ("Financial Risk", "Medium" if financials.debt_equity > 2 else "Low", "Leverage within acceptable limits"),
            ("Management Risk", "Low" if recommendation.five_cs.character > 70 else "High", "Experienced promoters"),
            ("Regulatory Risk", "Low", "No major regulatory changes expected")
        ]
        
        for risk, level, desc in risks:
            color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(level, "⚪")
            with st.expander(f"{color} {risk}: {level}"):
                st.write(desc)
    
    with cam_tabs[3]:
        st.markdown("#### Download CAM Document")
        
        # Generate Word-like content
        cam_content = f"""
CREDIT APPRAISAL MEMO

Borrower: {company.name}
Date: {datetime.now().strftime('%d-%b-%Y')}

RECOMMENDATION: {recommendation.decision}
Limit: Rs. {recommendation.limit_cr} Crores
Rate: {recommendation.interest_rate}% p.a.

This memo is generated by Intelli-Credit AI Engine.
        """
        
        st.download_button(
            label="📥 Download CAM (Word)",
            data=cam_content,
            file_name=f"CAM_{company.cin[:6]}_{datetime.now().strftime('%Y%m%d')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        st.download_button(
            label="📥 Download CAM (PDF)",
            data=cam_content,
            file_name=f"CAM_{company.cin[:6]}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

def main():
    """Main application entry point"""
    
    # Initialize components
    engine = CreditDecisioningEngine()
    mock_gen = MockDataGenerator()
    
    # Render UI
    render_header()
    page, risk_profile = render_sidebar()
    
    # Generate demo company based on risk profile
    company, financials = mock_gen.generate_company(risk_profile.split('_')[0])
    
    # Route to appropriate page
    if page == "📊 Dashboard":
        render_dashboard(engine, mock_gen)
    
    elif page == "📁 Data Ingestion":
        render_data_ingestion(engine, mock_gen, risk_profile.split('_')[0])
    
    elif page == "🔍 Research Agent":
        render_research_agent(mock_gen, company, risk_profile.split('_')[0])
    
    elif page == "🧠 Credit Analysis":
        render_credit_analysis(engine, mock_gen, risk_profile.split('_')[0], company, financials)
    
    elif page == "📄 CAM Generator":
        # Need to recalculate for consistency
        news = mock_gen.generate_news(company.name, risk_profile.split('_')[0])
        litigation = mock_gen.generate_litigation(risk_profile.split('_')[0])
        five_cs = engine.calculate_five_cs(company, financials, news, litigation)
        circular_risk = engine.detect_circular_trading(pd.DataFrame())
        recommendation = engine.generate_recommendation(company, financials, five_cs, circular_risk)
        render_cam_generator(recommendation, company, financials)
    
    elif page == "⚙️ Settings":
        st.subheader("⚙️ Configuration")
        st.write("**AI Model Settings**")
        st.slider("Risk Tolerance Threshold", 0, 100, 60)
        st.slider("GST Weight in Scoring", 0.0, 1.0, 0.30)
        st.slider("News Sentiment Weight", 0.0, 1.0, 0.20)
        
        st.write("**Integration Settings**")
        st.text_input("Databricks Host", "dbc-intelli-credit.cloud.databricks.com")
        st.text_input("MCA API Key", "••••••••", type="password")
        st.text_input("CIBIL API Endpoint", "https://api.cibil.com/commercial")

if __name__ == "__main__":
    main()
