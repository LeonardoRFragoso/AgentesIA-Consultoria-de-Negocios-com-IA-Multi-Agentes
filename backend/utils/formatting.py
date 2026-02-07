import streamlit as st


def display_agent_response(agent_name: str, title: str, content: str, emoji: str = ""):
    with st.expander(f"{emoji} {title}", expanded=False):
        st.markdown(content)


def display_executive_summary(content: str):
    st.markdown("---")
    st.markdown("## 👔 Diagnóstico Executivo Consolidado")
    st.markdown(content)
    st.markdown("---")


def display_loading_state(message: str):
    with st.spinner(message):
        pass


def format_report_for_export(results: dict) -> str:
    report = """
# Relatório de Análise de Negócio - Multi-Agentes

## 📋 Diagnóstico Executivo
"""
    report += results.get("executive", "")
    report += """

---

## 🔍 Análise Detalhada por Agente

### 1. Analista de Negócio
"""
    report += results.get("analyst", "")
    report += """

### 2. Estrategista Comercial
"""
    report += results.get("commercial", "")
    report += """

### 3. Analista Financeiro
"""
    report += results.get("financial", "")
    report += """

### 4. Especialista de Mercado
"""
    report += results.get("market", "")
    
    return report
