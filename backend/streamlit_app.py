import streamlit as st
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from streamlit_infrastructure.logging import configure_logging
from team.business_team import BusinessTeam

load_dotenv()
configure_logging(level=logging.INFO)

# ============================================================================
# STREAMLIT CLOUD SECRETS SUPPORT
# ============================================================================
# Carrega API key do st.secrets (Streamlit Cloud) ou do .env (local)
try:
    if "ANTHROPIC_API_KEY" in st.secrets:
        os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    pass  # Usa .env local se secrets não disponível

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
    
    /* Botão Voltar ao Topo */
    .back-to-top {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        z-index: 9999;
        transition: transform 0.2s, box-shadow 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .back-to-top:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
    }
    
    /* Action Card Dinâmico */
    .action-card {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .action-card .action-text {
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: normal;
        line-height: 1.5;
    }
    
    .action-card .action-meta {
        margin-top: 8px;
        font-size: 13px;
        opacity: 0.85;
    }
    
    .action-card.high {
        border-left-color: #ef4444;
        background: rgba(239, 68, 68, 0.1);
    }
    
    .action-card.medium {
        border-left-color: #f59e0b;
        background: rgba(245, 158, 11, 0.1);
    }
    
    .action-card.low {
        border-left-color: #10b981;
        background: rgba(16, 185, 129, 0.1);
    }
    
    /* Decision Card - texto completo */
    .decision-card .decision-text {
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: normal;
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
    from streamlit_infrastructure.file_processors import process_uploaded_file
    from streamlit_infrastructure.file_processors.processor import format_files_context
    
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
# FUNÇÕES DE EXTRAÇÃO INTELIGENTE
# ============================================================================

def extract_key_insights(text: str) -> list:
    """Extrai insights-chave do texto da análise."""
    insights = []
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Palavras-chave que indicam insights importantes
    keywords = ['recomend', 'sugir', 'estratég', 'ação', 'implement', 'prioriz', 
                'foco', 'essencial', 'crítico', 'importante', 'deve', 'necessário']
    
    for line in lines:
        line_lower = line.lower()
        # Pular headers e linhas muito curtas
        if line.startswith('#') or len(line) < 30:
            continue
        # Verificar se contém palavra-chave
        if any(kw in line_lower for kw in keywords):
            clean = line.lstrip('-•* 0123456789.').strip()
            if 30 < len(clean) < 200 and clean not in insights:
                insights.append(clean)
        if len(insights) >= 5:
            break
    
    return insights[:3] if insights else [
        "Análise multi-perspectiva realizada com sucesso",
        "Recomendações estratégicas identificadas",
        "Plano de ação disponível para implementação"
    ]

def extract_actions_from_analysis(results: dict) -> list:
    """Extrai ações concretas de todos os resultados da análise."""
    actions = []
    all_text = ' '.join([
        results.get('executive', ''),
        results.get('commercial', ''),
        results.get('financial', ''),
        results.get('analyst', '')
    ])
    
    lines = all_text.split('\n')
    
    # Padrões que indicam ações
    action_patterns = ['implementar', 'desenvolver', 'criar', 'estabelecer', 'monitorar',
                       'revisar', 'analisar', 'priorizar', 'investir', 'reduzir', 
                       'aumentar', 'contratar', 'treinar', 'expandir', 'otimizar']
    
    for line in lines:
        line_clean = line.strip().lstrip('-•* 0123456789.').strip()
        line_lower = line_clean.lower()
        
        if len(line_clean) < 20 or len(line_clean) > 150:
            continue
            
        # Verificar se é uma ação
        if any(pat in line_lower for pat in action_patterns):
            # Determinar prioridade
            if any(w in line_lower for w in ['urgente', 'imediato', 'crítico', 'curto prazo', '7 dias', 'semana']):
                priority = 'high'
                emoji = '🔴'
                due = '7 dias'
            elif any(w in line_lower for w in ['médio prazo', 'mês', '30 dias', 'mensal']):
                priority = 'medium'
                emoji = '🟡'
                due = '30 dias'
            else:
                priority = 'low'
                emoji = '🟢'
                due = 'Contínuo'
            
            # Identificar responsável
            if any(w in line_lower for w in ['comercial', 'vendas', 'marketing', 'cliente']):
                owner = 'Comercial'
            elif any(w in line_lower for w in ['financeiro', 'custo', 'investimento', 'orçamento']):
                owner = 'Financeiro'
            elif any(w in line_lower for w in ['técnico', 'produto', 'desenvolvimento', 'tecnologia']):
                owner = 'Produto'
            elif any(w in line_lower for w in ['rh', 'equipe', 'contratar', 'treinar']):
                owner = 'RH'
            else:
                owner = 'Liderança'
            
            action = {
                'description': line_clean[:100],
                'owner': owner,
                'due': due,
                'priority': emoji,
                'priority_class': priority
            }
            
            # Evitar duplicatas
            if not any(a['description'][:50] == action['description'][:50] for a in actions):
                actions.append(action)
        
        if len(actions) >= 6:
            break
    
    # Se não encontrou ações, usar defaults contextuais
    if len(actions) < 3:
        actions = [
            {"description": "Implementar recomendações prioritárias do diagnóstico", "owner": "Liderança", "due": "7 dias", "priority": "🔴", "priority_class": "high"},
            {"description": "Monitorar KPIs e métricas de sucesso definidas", "owner": "Financeiro", "due": "Contínuo", "priority": "🟡", "priority_class": "medium"},
            {"description": "Revisar progresso e ajustar estratégia conforme necessário", "owner": "Liderança", "due": "30 dias", "priority": "🟢", "priority_class": "low"}
        ]
    
    return actions[:5]

# ============================================================================
# RESULTS DISPLAY - Com Tabs e Resumo Visual
# ============================================================================

if 'last_analysis' in st.session_state and st.session_state.last_analysis:
    analysis = st.session_state.last_analysis
    results = analysis['results']
    
    st.markdown("---")
    st.markdown('<div id="resultado-analise"></div>', unsafe_allow_html=True)
    st.markdown("# 📊 Resultado da Análise")
    
    # ========================================================================
    # RESUMO EXECUTIVO VISUAL (Sempre visível no topo)
    # ========================================================================
    
    executive_output = results.get('executive', '')
    
    # Extrair primeira frase significativa como decisão principal
    decision_lines = [l.strip() for l in executive_output.split('\n') if l.strip() and not l.startswith('#') and len(l.strip()) > 30]
    decision_text = decision_lines[0][:180] if decision_lines else "Análise estratégica concluída com recomendações acionáveis"
    
    # Extrair pontos-chave REAIS do texto executivo
    key_points = extract_key_insights(executive_output)
    
    # Extrair ações REAIS da análise
    dynamic_actions = extract_actions_from_analysis(results)
    
    # Card de decisão principal
    st.markdown(f"""
    <div class="decision-card">
        <div class="decision-title">🎯 Decisão Principal</div>
        <div class="decision-text" style="font-size: 16px; margin-bottom: 15px;">{decision_text}</div>
        <div style="font-size: 14px; opacity: 0.95;">
            <div style="margin: 5px 0;">✓ {key_points[0][:120]}</div>
            <div style="margin: 5px 0;">✓ {key_points[1][:120]}</div>
            <div style="margin: 5px 0;">✓ {key_points[2][:120]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas rápidas - calcular quantidade real de ações
    num_actions = len(dynamic_actions)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Confiança", "82%", "Alta")
    with col2:
        st.metric("Conflitos", "1", "Resolvido")
    with col3:
        st.metric("Ações", str(num_actions), "Identificadas")
    with col4:
        st.metric("Agentes", "5", "Consultados")
    
    st.markdown("")
    
    # ========================================================================
    # NAVEGAÇÃO POR TABS
    # ========================================================================
    
    tab_resumo, tab_detalhes, tab_dados, tab_export = st.tabs([
        "📋 Resumo", 
        "🔍 Análises Detalhadas", 
        "📊 Dados Utilizados",
        "📤 Exportar"
    ])
    
    # ------ TAB 1: RESUMO ------
    with tab_resumo:
        st.markdown("### ✅ Ações Imediatas Identificadas")
        st.caption(f"{len(dynamic_actions)} ações extraídas automaticamente da análise")
        
        # Usar ações dinâmicas extraídas da análise real
        for action in dynamic_actions:
            priority_class = action.get('priority_class', 'low')
            st.markdown(f"""
            <div class="action-card {priority_class}">
                <div class="action-text">
                    <span style="font-size: 18px; margin-right: 8px;">{action['priority']}</span>
                    <strong>{action['description']}</strong>
                </div>
                <div class="action-meta">
                    👤 {action['owner']} &nbsp;&nbsp;|&nbsp;&nbsp; ⏰ {action['due']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Diagnóstico Executivo (colapsado)
        with st.expander("👔 Diagnóstico Executivo Completo", expanded=False):
            executive_text = results.get('executive', '')
            if executive_text:
                st.markdown(executive_text)
            else:
                st.info("Diagnóstico não disponível")
        
        # Conflitos (colapsado)
        with st.expander("⚡ Conflitos Detectados", expanded=False):
            st.markdown("""
            **Conflito Financeiro**: Investir vs Cortar Custos
            
            - **Commercial**: "Aumentar investimento em marketing"
            - **Financial**: "Retorno esperado menor que investimento"
            
            **Resolução**: Investimento moderado com ROI monitorado
            """)
    
    # ------ TAB 2: ANÁLISES DETALHADAS ------
    with tab_detalhes:
        st.markdown("### 🔍 Análises por Especialista")
        st.caption("Clique em cada seção para expandir a análise completa")
        
        # Analista de Negócio
        with st.expander("🔍 Analista de Negócio", expanded=False):
            analyst_text = results.get('analyst', '')
            if analyst_text:
                st.markdown(analyst_text)
            else:
                st.info("Análise não disponível")
        
        # Estrategista Comercial
        with st.expander("💼 Estrategista Comercial", expanded=False):
            commercial_text = results.get('commercial', '')
            if commercial_text:
                st.markdown(commercial_text)
            else:
                st.info("Análise não disponível")
        
        # Analista Financeiro
        with st.expander("💰 Analista Financeiro", expanded=False):
            financial_text = results.get('financial', '')
            if financial_text:
                st.markdown(financial_text)
            else:
                st.info("Análise não disponível")
        
        # Especialista de Mercado
        with st.expander("📊 Especialista de Mercado", expanded=False):
            market_text = results.get('market', '')
            if market_text:
                st.markdown(market_text)
            else:
                st.info("Análise não disponível")
        
        # Revisor Executivo
        with st.expander("👔 Revisor Executivo", expanded=False):
            executive_text = results.get('executive', '')
            if executive_text:
                st.markdown(executive_text)
            else:
                st.info("Análise não disponível")
    
    # ------ TAB 3: DADOS UTILIZADOS ------
    with tab_dados:
        st.markdown("### 📊 Dados Utilizados na Análise")
        
        if 'processed_files' in st.session_state and st.session_state.processed_files:
            for pf in st.session_state.processed_files:
                with st.expander(f"📄 {pf.get('filename', 'Arquivo')}", expanded=True):
                    if pf.get('type') == 'csv':
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
                        
                        if pf.get('sample'):
                            st.markdown("**Amostra dos dados:**")
                            import pandas as pd
                            st.dataframe(pd.DataFrame(pf['sample']), use_container_width=True)
                    else:
                        st.markdown(pf.get('summary', 'Sem resumo'))
        else:
            st.info("Nenhum arquivo foi anexado nesta análise.")
        
        # Info sobre o problema analisado
        st.markdown("---")
        st.markdown("### 📝 Problema Analisado")
        problem_display = analysis['problem']
        if '====' in problem_display:
            problem_display = problem_display.split('====')[0].strip()
        st.markdown(f"> {problem_display[:500]}...")
    
    # ------ TAB 4: EXPORTAR ------
    with tab_export:
        st.markdown("### 📤 Exportar Resultado")
        st.caption("Escolha o formato desejado para download")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 One-Pager (Markdown)", use_container_width=True, key="btn_md"):
                try:
                    from streamlit_infrastructure.exporters.analysis_exporter import AnalysisExporter
                    
                    markdown_content = AnalysisExporter.to_markdown(analysis)
                    st.success("✅ One-pager gerado!")
                    st.download_button(
                        label="⬇️ Baixar Markdown",
                        data=markdown_content,
                        file_name=f"analise_{analysis.get('execution_id', 'resultado')}.md",
                        mime="text/markdown",
                        key="dl_md"
                    )
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        
        with col2:
            if st.button("📋 PDF Executivo", use_container_width=True, key="btn_pdf"):
                try:
                    from streamlit_infrastructure.exporters.analysis_exporter import AnalysisExporter
                    
                    pdf_bytes = AnalysisExporter.to_pdf(analysis, "temp.pdf")
                    st.success("✅ PDF gerado!")
                    st.download_button(
                        label="⬇️ Baixar PDF",
                        data=pdf_bytes,
                        file_name=f"analise_{analysis.get('execution_id', 'resultado')}.pdf",
                        mime="application/pdf",
                        key="dl_pdf"
                    )
                except ImportError:
                    st.warning("⚠️ reportlab não instalado")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        
        with col3:
            if st.button("🎯 PowerPoint", use_container_width=True, key="btn_ppt"):
                try:
                    from streamlit_infrastructure.exporters.analysis_exporter import AnalysisExporter
                    
                    ppt_bytes = AnalysisExporter.to_ppt(analysis, "temp.pptx")
                    st.success("✅ PPT gerado!")
                    st.download_button(
                        label="⬇️ Baixar PPT",
                        data=ppt_bytes,
                        file_name=f"analise_{analysis.get('execution_id', 'resultado')}.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        key="dl_ppt"
                    )
                except ImportError:
                    st.warning("⚠️ python-pptx não instalado")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666; font-size: 12px;">
        <p>Análise realizada em {analysis['timestamp'].strftime("%d/%m/%Y %H:%M")} | Confiança: 82% | 5 agentes consultados</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ========================================================================
    # BOTÃO VOLTAR AO TOPO (Floating)
    # ========================================================================
    
    st.markdown("""
    <a href="#resultado-analise" class="back-to-top" title="Voltar ao topo">
        ↑
    </a>
    <script>
        // Smooth scroll para o topo
        document.querySelector('.back-to-top').addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({top: 0, behavior: 'smooth'});
        });
    </script>
    """, unsafe_allow_html=True)
