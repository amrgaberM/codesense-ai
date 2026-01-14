import streamlit as st
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

st.set_page_config(page_title="CodeSense AI", page_icon="", layout="wide")

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .block-container {
        padding: 2rem 4rem;
        max-width: 1400px;
    }
    
    .main-header {
        padding: 30px 0;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 30px;
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 32px;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        font-size: 14px;
        color: #a1a1aa;
        margin: 8px 0 0 0;
    }
    
    .section-title {
        font-size: 12px;
        font-weight: 600;
        color: #e5e7eb;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    
    .stTextArea textarea {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px;
        background: #1e1e1e;
        color: #d4d4d4;
        border: 1px solid #2d2d2d;
        border-radius: 8px;
    }
    
    .stButton > button {
        font-size: 13px;
        font-weight: 500;
        padding: 10px 20px;
        border-radius: 6px;
        transition: all 0.2s;
    }
    
    .stButton > button[data-baseweb="button"] {
        background: #3b82f6;
        color: white;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59,130,246,0.4);
    }
    
    .metric-container {
        display: flex;
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .metric-box {
        flex: 1;
        background: #27272a;
        border: 1px solid #3f3f46;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
    }
    
    .metric-label {
        font-size: 12px;
        color: #a1a1aa;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .severity-critical {
        background: #450a0a;
        border-left: 4px solid #dc2626;
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0;
    }
    
    .severity-high {
        background: #431407;
        border-left: 4px solid #ea580c;
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0;
    }
    
    .severity-medium {
        background: #422006;
        border-left: 4px solid #ca8a04;
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0;
    }
    
    .severity-low {
        background: #0c4a6e;
        border-left: 4px solid #0284c7;
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0;
    }
    
    .severity-critical, .severity-high, .severity-medium, .severity-low {
        color: #ffffff;
    }
    
    .severity-critical p, .severity-high p, .severity-medium p, .severity-low p {
        color: #d4d4d8 !important;
    }
    
    .badge {
        display: inline-block;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 600;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .badge-critical { background: #dc2626; color: #ffffff; }
    .badge-high { background: #ea580c; color: #ffffff; }
    .badge-medium { background: #ca8a04; color: #ffffff; }
    .badge-low { background: #0284c7; color: #ffffff; }
    
    .empty-state {
        text-align: center;
        padding: 60px 20px;
    }
    
    .empty-state h3 {
        font-size: 16px;
        font-weight: 500;
        color: #a1a1aa;
        margin-bottom: 8px;
    }
    
    .empty-state p {
        font-size: 13px;
        color: #71717a;
    }
    
    .footer {
        margin-top: 60px;
        padding: 24px 0;
        border-top: 1px solid #3f3f46;
        text-align: center;
    }
    
    .footer p {
        font-size: 13px;
        color: #71717a;
        margin: 4px 0;
    }
    
    .footer a {
        color: #a1a1aa;
        text-decoration: none;
        margin: 0 12px;
    }
    
    .footer a:hover {
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class='main-header'>
    <h1>CodeSense AI</h1>
    <p>Static Analysis & Security Review Platform</p>
</div>
""", unsafe_allow_html=True)

# Layout
col_input, col_space, col_output = st.columns([5, 0.5, 6])

with col_input:
    st.markdown("<p class='section-title'>Input</p>", unsafe_allow_html=True)
    
    code = st.text_area(
        label="source",
        label_visibility="collapsed",
        height=500,
        placeholder="// Enter source code for analysis"
    )
    
    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        full_btn = st.button("Full Analysis", use_container_width=True, type="primary")
    with c2:
        sec_btn = st.button("Security Scan", use_container_width=True)
    with c3:
        quick_btn = st.button("Quick Scan", use_container_width=True)

with col_output:
    st.markdown("<p class='section-title'>Analysis Report</p>", unsafe_allow_html=True)
    
    if full_btn or sec_btn or quick_btn:
        if code:
            with st.spinner("Analyzing..."):
                from groq import Groq
                client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
                
                json_format = '''Respond ONLY with valid JSON in this exact format:
{
    "language": "detected language",
    "summary": "one line summary",
    "score": 85,
    "issues": [
        {
            "severity": "critical|high|medium|low",
            "title": "Issue title",
            "description": "Detailed description",
            "line": 1,
            "suggestion": "How to fix"
        }
    ],
    "recommendations": ["recommendation 1", "recommendation 2"]
}'''
                
                if sec_btn:
                    focus = "Focus on security vulnerabilities only: injection, XSS, hardcoded secrets, auth issues."
                elif quick_btn:
                    focus = "List only top 3 most critical issues. Be brief."
                else:
                    focus = "Comprehensive analysis: security, bugs, performance, best practices."
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"You are a code analyzer. {focus}\n\n{json_format}"},
                        {"role": "user", "content": f"Analyze:\n\n{code}"}
                    ],
                    temperature=0.1
                )
                
                content = response.choices[0].message.content
                
                try:
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        data = json.loads(json_match.group())
                    else:
                        data = json.loads(content)
                    
                    # Metrics
                    st.markdown(f"""
                    <div class='metric-container'>
                        <div class='metric-box'>
                            <div class='metric-value'>{data.get('score', 'N/A')}</div>
                            <div class='metric-label'>Quality Score</div>
                        </div>
                        <div class='metric-box'>
                            <div class='metric-value'>{len(data.get('issues', []))}</div>
                            <div class='metric-label'>Issues Found</div>
                        </div>
                        <div class='metric-box'>
                            <div class='metric-value'>{data.get('language', 'N/A').upper()}</div>
                            <div class='metric-label'>Language</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if data.get('summary'):
                        st.markdown(f"**Summary:** {data['summary']}")
                    
                    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
                    
                    if data.get('issues'):
                        for issue in data['issues']:
                            severity = issue.get('severity', 'medium').lower()
                            st.markdown(f"""
                            <div class='severity-{severity}'>
                                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                                    <strong style='color: #ffffff;'>{issue.get('title', 'Issue')}</strong>
                                    <span class='badge badge-{severity}'>{severity}</span>
                                </div>
                                <p style='margin: 0 0 8px 0; font-size: 14px;'>{issue.get('description', '')}</p>
                                {f"<p style='margin: 0; font-size: 13px;'><strong>Line:</strong> {issue.get('line')}</p>" if issue.get('line') else ""}
                                {f"<p style='margin: 8px 0 0 0; font-size: 13px; color: #4ade80 !important;'><strong>Fix:</strong> {issue.get('suggestion')}</p>" if issue.get('suggestion') else ""}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    if data.get('recommendations'):
                        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
                        st.markdown("**Recommendations**")
                        for rec in data['recommendations']:
                            st.markdown(f"- {rec}")
                            
                except Exception as e:
                    st.markdown(content)
        else:
            st.error("Please enter code to analyze.")
    else:
        st.markdown("""
        <div class='empty-state'>
            <h3>No Analysis Yet</h3>
            <p>Enter your source code and select an analysis type to begin</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class='footer'>
    <p>CodeSense AI - Automated Code Analysis Platform</p>
    <p>
        <a href='https://github.com/amrgaberM/codesense-ai'>Documentation</a>
        <a href='https://github.com/amrgaberM'>GitHub</a>
        <a href='https://linkedin.com/in/amrhassangaber'>LinkedIn</a>
    </p>
</div>
""", unsafe_allow_html=True)
