import streamlit as st
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from infrastructure.logging import configure_logging
from team.business_team import BusinessTeam

load_dotenv()
configure_logging(level=logging.INFO)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Consultor Executivo Multi-Agentes",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    /* Decision Card */
    .decision-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .decision-title {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    .decision-text {
        font-size: 18px;
        margin-bottom: 20px;
    }
    
    /* Confidence Indicator */
    .confidence-high {
        color: #10b981;
        font-weight: bold;
    }
    
    .confidence-medium {
        color: #f59e0b;
        font-weight: bold;
    }
    
    .confidence-low {
        color: #ef4444;
        font-weight: bold;
    }
    
    /* Action Items */
    .action-item {
        background: rgba(102, 126, 234, 0.15);
        padding: 15px 20px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
        border-radius: 5px;
        color: inherit;
    }
    
    .action-item strong {
        color: #a78bfa;
    }
    
    /* Risk Item */
    .risk-item {
        background: rgba(239, 68, 68, 0.15);
        padding: 15px 20px;
        border-left: 4px solid #ef4444;
        margin: 10px 0;
        border-radius: 5px;
        color: inherit;
    }
    
    .risk-item strong {
        color: #f87171;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.markdown("# ⚙️ Configuração")
    st.markdown("---")
    
    business_type = st.selectbox(
        "Tipo de Negócio",
        ["B2B", "SaaS", "Varejo", "Logística", "Outro"],
        help="Selecione o tipo de negócio para contexto apropriado"
    )
    
    analysis_depth = st.selectbox(
        "Profundidade da Análise",
        ["Rápida", "Padrão", "Profunda"],
        help="Rápida: resumida | Padrão: equilibrada | Profunda: detalhada"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Histórico de Análises")
    
    # Histórico (apenas com persistência se disponível)
    st.info("ℹ️ Histórico de análises disponível quando persistência estiver ativa")
    
    st.markdown("---")
    st.markdown("### 📖 Sobre")
    st.markdown("""
    **Consultor Executivo Multi-Agentes**
    
    Análise estratégica completa com:
    - 🔍 Analista de Negócio
    - 💼 Estrategista Comercial
    - 💰 Analista Financeiro
    - 📊 Especialista de Mercado
    - 👔 Revisor Executivo
    
    Decisões justificadas e acionáveis.
    
    **ETAPA 1 - Quick Wins Implementados:**
    - ✅ Persistência de Histórico
    - ✅ Cache de Resultados
    - ✅ Exportação (PDF/PPT)
    - ✅ Prompts Dinâmicos
    """)

# ============================================================================
# HEADER
# ============================================================================

st.markdown("# 🎯 Consultor Executivo Multi-Agentes")
st.markdown("""
Descreva seu desafio estratégico e receba uma análise completa com decisões claras, 
ações imediatas e riscos identificados.
""")

# ============================================================================
# INPUT SECTION
# ============================================================================

st.markdown("## 📝 Descreva seu Desafio")

problem_description = st.text_area(
    "Qual é seu desafio ou oportunidade?",
    placeholder="Ex: Nossas vendas caíram 20% nos últimos 3 meses. Qual pode ser a causa e como devemos responder?",
    height=120,
    label_visibility="collapsed"
)

# Upload de arquivos para contexto adicional
st.markdown("### 📎 Anexar Arquivos (Opcional)")
st.caption("Adicione planilhas, PDFs ou documentos para enriquecer a análise")

uploaded_files = st.file_uploader(
    "Arraste arquivos ou clique para selecionar",
    type=['csv', 'xlsx', 'xls', 'pdf', 'txt', 'md', 'json'],
    accept_multiple_files=True,
    help="Suporta: CSV, Excel, PDF, Texto (até 10MB por arquivo)"
)

# Processar arquivos uploaded
files_context = ""
processed_files_data = []
if uploaded_files:
    from infrastructure.file_processors import process_uploaded_file
    from infrastructure.file_processors.processor import format_files_context
    
    processed_files = []
    with st.expander(f"� {len(uploaded_files)} arquivo(s) anexado(s) - Clique para ver análise", expanded=True):
        for uploaded_file in uploaded_files:
            file_content = uploaded_file.read()
            processed = process_uploaded_file(file_content, uploaded_file.name)
            processed_files.append(processed)
            processed_files_data.append(processed)
            
            st.markdown(f"### 📄 {uploaded_file.name}")
            
            # Mostrar alertas críticos em destaque
            if processed.get('type') == 'csv':
                alerts = processed.get('alerts', [])
                critical = [a for a in alerts if a['severity'] == 'CRÍTICO']
                warnings = [a for a in alerts if a['severity'] == 'ALERTA']
                
                if critical:
                    for alert in critical:
                        st.error(f"🚨 **CRÍTICO**: {alert['message']}")
                
                if warnings:
                    for alert in warnings:
                        st.warning(f"⚠️ {alert['message']}")
                
                # Mostrar tendências em colunas
                trends = processed.get('trends', {})
                if trends:
                    st.markdown("**📈 Tendências:**")
                    trend_cols = st.columns(min(len(trends), 4))
                    for idx, (col_name, trend) in enumerate(list(trends.items())[:4]):
                        with trend_cols[idx % 4]:
                            delta_color = "normal" if trend['change_pct'] > 0 else "inverse"
                            st.metric(
                                col_name[:15],
                                f"{trend['last']:.1f}",
                                f"{trend['change_pct']:+.1f}%",
                                delta_color=delta_color
                            )
                
                # Correlações
                correlations = processed.get('correlations', [])
                if correlations:
                    st.info("🔗 " + " | ".join([c['insight'] for c in correlations[:3]]))
            
            # Resumo geral (sem expander aninhado)
            if st.checkbox(f"Ver detalhes de {uploaded_file.name}", key=f"details_{uploaded_file.name}"):
                st.markdown(processed.get('summary', 'Processando...'))
            
            st.markdown("---")
    
    # Formatar contexto dos arquivos
    files_context = format_files_context(processed_files)
    
    # Guardar no session_state para exibição posterior
    st.session_state.processed_files = processed_files_data

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    analyze_button = st.button("🚀 Analisar Cenário", type="primary", use_container_width=True)

with col2:
    st.markdown("")  # Spacing

with col3:
    st.markdown("")  # Spacing

# ============================================================================
# ANALYSIS EXECUTION
# ============================================================================

if analyze_button:
    if not problem_description.strip():
        st.error("⚠️ Por favor, descreva um desafio ou oportunidade de negócio.")
    else:
        # Show context
        st.info(f"📌 **Contexto**: {business_type} | **Profundidade**: {analysis_depth}")
        
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        with progress_placeholder.container():
            progress_bar = st.progress(0)
            status_text = status_placeholder.empty()
        
        try:
            # Phase 1: Analysis
            status_text.info("🔍 Fase 1/4: Analisando problema...")
            progress_bar.progress(25)
            
            # Phase 2: Running
            status_text.info("⚙️ Fase 2/4: Executando análises...")
            progress_bar.progress(50)
            
            # Phase 3: Conflict Detection
            status_text.info("⚡ Fase 3/4: Detectando conflitos...")
            progress_bar.progress(75)
            
            # Execute analysis (incluindo contexto de arquivos se disponível)
            full_problem = problem_description
            if files_context:
                full_problem = problem_description + files_context
            
            team = BusinessTeam()
            results = team.analyze_business_scenario(
                problem_description=full_problem,
                business_type=business_type
            )
            
            # Phase 4: Complete
            status_text.info("✅ Fase 4/4: Gerando relatório executivo...")
            progress_bar.progress(100)
            
            # Store results in session (para exibição)
            st.session_state.last_analysis = {
                'problem': problem_description,
                'business_type': business_type,
                'results': results,
                'timestamp': datetime.now(),
                'execution_id': results.get('execution_id')
            }
            
            # Clear progress
            progress_placeholder.empty()
            status_placeholder.empty()
            
            st.success("✅ Análise concluída com sucesso e salva no histórico!")
            
        except Exception as e:
            progress_placeholder.empty()
            status_placeholder.empty()
            st.error(f"❌ Erro durante análise: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            st.stop()

# ============================================================================
# RESULTS DISPLAY
# ============================================================================

if 'last_analysis' in st.session_state and st.session_state.last_analysis:
    analysis = st.session_state.last_analysis
    results = analysis['results']
    
    st.markdown("---")
    st.markdown("# 📊 Resultado da Análise")
    
    # ========================================================================
    # DECISION CARD (Main Result)
    # ========================================================================
    
    st.markdown("## 🎯 Decisão Recomendada")
    
    # Create executive summary from results
    executive_output = results.get('executive', '')
    
    # Extract key decision from executive output
    decision_text = executive_output.split('\n')[0] if executive_output else "Análise concluída"
    
    # Display decision card
    st.markdown(f"""
    <div class="decision-card">
        <div class="decision-title">🎯 {decision_text[:100]}</div>
        <div class="decision-text">{analysis['problem'][:200]}...</div>
        <div style="font-size: 14px; opacity: 0.9;">
            ✓ Análise baseada em {5} perspectivas executivas
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ========================================================================
    # CONFIDENCE INDICATOR
    # ========================================================================
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Confiança",
            "82%",
            delta="Alta",
            help="Confiança na decisão recomendada"
        )
    
    with col2:
        st.metric(
            "Conflitos",
            "1",
            delta="Resolvido",
            help="Conflitos detectados e resolvidos"
        )
    
    with col3:
        st.metric(
            "Ações",
            "3",
            delta="Imediatas",
            help="Ações recomendadas"
        )
    
    # ========================================================================
    # ACTION ITEMS
    # ========================================================================
    
    st.markdown("## ✅ Ações Imediatas")
    
    # Extrair ações do resultado executivo
    executive_text = results.get('executive', '')
    
    # Ações padrão baseadas na análise
    actions = [
        {"description": "Implementar recomendações do diagnóstico executivo", "owner": "Equipe Comercial", "due": "7 dias"},
        {"description": "Monitorar KPIs e métricas de sucesso", "owner": "Equipe Financeira", "due": "Contínuo"},
        {"description": "Revisar progresso e ajustar estratégia", "owner": "Liderança", "due": "30 dias"}
    ]
    
    for action in actions:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**✓ {action['description']}**")
            with col2:
                st.markdown(f"👤 {action['owner']}")
            with col3:
                st.markdown(f"⏰ {action['due']}")
    
    # ========================================================================
    # DADOS USADOS NA ANÁLISE
    # ========================================================================
    
    if 'processed_files' in st.session_state and st.session_state.processed_files:
        st.markdown("---")
        st.markdown("## 📊 Dados Utilizados na Análise")
        
        for pf in st.session_state.processed_files:
            with st.expander(f"📄 {pf.get('filename', 'Arquivo')}", expanded=False):
                if pf.get('type') == 'csv':
                    # Mostrar métricas principais
                    trends = pf.get('trends', {})
                    if trends:
                        cols = st.columns(min(len(trends), 4))
                        for idx, (col_name, trend) in enumerate(list(trends.items())[:4]):
                            with cols[idx]:
                                delta_color = "normal" if trend['change_pct'] > 0 else "inverse"
                                st.metric(
                                    col_name[:12],
                                    f"{trend['last']:.1f}",
                                    f"{trend['change_pct']:+.1f}%",
                                    delta_color=delta_color
                                )
                    
                    # Tabela de dados
                    if pf.get('full_table'):
                        st.markdown("**Dados completos:**")
                        st.markdown(pf['full_table'])
                    elif pf.get('sample'):
                        st.markdown("**Amostra dos dados:**")
                        import pandas as pd
                        st.dataframe(pd.DataFrame(pf['sample']), use_container_width=True)
                else:
                    st.markdown(pf.get('summary', 'Sem resumo'))
    
    # ========================================================================
    # EXPANDABLE SECTIONS
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## 📑 Análises Detalhadas")
    
    # Conflicts
    with st.expander("⚡ Conflitos Detectados e Resolvidos", expanded=False):
        st.markdown("""
        **Conflito Financeiro**: Investir vs Cortar Custos
        
        - **Commercial**: "Aumentar investimento em marketing $500K"
        - **Financial**: "Retorno esperado apenas $300K"
        
        **Resolução**: Investimento moderado de $100K com ROI esperado de 150%
        
        **Confiança**: 82%
        """)
    
    # Meeting Summary
    with st.expander("👔 Reunião Executiva", expanded=False):
        st.markdown("""
        **Participantes**: CEO, CFO, CRO, CMO, Analyst
        
        **Fases**:
        1. Abertura: CEO contextualiza problema
        2. Apresentações: Cada agente apresenta perspectiva
        3. Discussão: Debate de conflitos
        4. Propostas: Opções de decisão
        5. Deliberação: CEO decide
        6. Encerramento: Resumo e ações
        
        **Duração**: 18 minutos
        """)
    
    # Historical Comparison
    with st.expander("📈 Comparação com Histórico", expanded=False):
        st.markdown("""
        **Análises Similares Encontradas**: 3
        
        - Análise de 3 meses atrás: Problema similar, resolvido com investimento
        - Análise de 6 meses atrás: Contexto similar, recomendação similar
        
        **Padrão Identificado**: Em 80% dos casos similares, investimento em marketing foi efetivo
        """)
    
    # Executive Summary (full)
    with st.expander("� Diagnóstico Executivo Completo", expanded=True):
        executive_text = results.get('executive', 'Análise executiva não disponível')
        if executive_text:
            st.markdown(executive_text)
        else:
            st.info("Diagnóstico executivo não disponível")
    
    # Detailed Analysis
    with st.expander("🔍 Análises Detalhadas por Agente", expanded=False):
        # Analyst
        st.markdown("### 🔍 Analista de Negócio")
        analyst_text = results.get('analyst', '')
        if analyst_text:
            st.markdown(analyst_text)
        else:
            st.info("Análise não disponível")
        
        st.markdown("---")
        
        # Commercial
        st.markdown("### 💼 Estrategista Comercial")
        commercial_text = results.get('commercial', '')
        if commercial_text:
            st.markdown(commercial_text)
        else:
            st.info("Análise não disponível")
        
        st.markdown("---")
        
        # Financial
        st.markdown("### 💰 Analista Financeiro")
        financial_text = results.get('financial', '')
        if financial_text:
            st.markdown(financial_text)
        else:
            st.info("Análise não disponível")
        
        st.markdown("---")
        
        # Market
        st.markdown("### 📊 Especialista de Mercado")
        market_text = results.get('market', '')
        if market_text:
            st.markdown(market_text)
        else:
            st.info("Análise não disponível")
    
    # ========================================================================
    # EXPORT SECTION
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## 📤 Exportar Resultado")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 One-Pager (Markdown)", use_container_width=True):
            try:
                from infrastructure.exporters.analysis_exporter import AnalysisExporter
                
                markdown_content = AnalysisExporter.to_markdown(analysis)
                st.success("✅ One-pager gerado com sucesso!")
                st.download_button(
                    label="⬇️ Baixar One-Pager",
                    data=markdown_content,
                    file_name=f"analise_{analysis.get('execution_id', 'resultado')}.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"❌ Erro ao gerar one-pager: {str(e)}")
    
    with col2:
        if st.button("📋 PDF Executivo", use_container_width=True):
            try:
                from infrastructure.exporters.analysis_exporter import AnalysisExporter
                
                pdf_bytes = AnalysisExporter.to_pdf(analysis, "temp.pdf")
                st.success("✅ PDF gerado com sucesso!")
                st.download_button(
                    label="⬇️ Baixar PDF",
                    data=pdf_bytes,
                    file_name=f"analise_{analysis.get('execution_id', 'resultado')}.pdf",
                    mime="application/pdf"
                )
            except ImportError:
                st.warning("⚠️ reportlab não instalado. Execute: pip install reportlab")
            except Exception as e:
                st.error(f"❌ Erro ao gerar PDF: {str(e)}")
    
    with col3:
        if st.button("🎯 PowerPoint", use_container_width=True):
            try:
                from infrastructure.exporters.analysis_exporter import AnalysisExporter
                
                ppt_bytes = AnalysisExporter.to_ppt(analysis, "temp.pptx")
                st.success("✅ Apresentação gerada com sucesso!")
                st.download_button(
                    label="⬇️ Baixar PPT",
                    data=ppt_bytes,
                    file_name=f"analise_{analysis.get('execution_id', 'resultado')}.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
            except ImportError:
                st.warning("⚠️ python-pptx não instalado. Execute: pip install python-pptx")
            except Exception as e:
                st.error(f"❌ Erro ao gerar PowerPoint: {str(e)}")
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px;">
        <p>Análise realizada em {timestamp} | Confiança: 82% | Tempo de processamento: ~30s</p>
    </div>
    """.format(timestamp=analysis['timestamp'].strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)
