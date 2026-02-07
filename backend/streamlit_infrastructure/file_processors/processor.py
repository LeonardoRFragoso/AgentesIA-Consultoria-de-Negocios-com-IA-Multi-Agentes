"""Processadores de arquivos para extração de conteúdo."""

import io
from typing import Dict, Optional, List, Any
from abc import ABC, abstractmethod


class FileProcessor(ABC):
    """Classe base para processadores de arquivo."""
    
    @abstractmethod
    def process(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Processa arquivo e extrai conteúdo.
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            filename: Nome do arquivo
        
        Returns:
            Dict com conteúdo extraído e metadados
        """
        pass
    
    @abstractmethod
    def supports(self, filename: str) -> bool:
        """Verifica se o processador suporta o tipo de arquivo."""
        pass


class CSVProcessor(FileProcessor):
    """Processa arquivos CSV com análise avançada de tendências e insights."""
    
    def supports(self, filename: str) -> bool:
        return filename.lower().endswith('.csv')
    
    def process(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extrai conteúdo de CSV com análise de tendências."""
        try:
            import pandas as pd
            
            # Detectar encoding
            content_str = file_content.decode('utf-8', errors='ignore')
            df = pd.read_csv(io.StringIO(content_str))
            
            # Extrair estatísticas básicas
            stats = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            }
            
            # Resumo estatístico para colunas numéricas
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                stats['numeric_summary'] = df[numeric_cols].describe().to_dict()
            
            # Análise de tendências (se houver dados temporais)
            trends = self._analyze_trends(df, numeric_cols)
            
            # Detectar alertas e anomalias
            alerts = self._detect_alerts(df, numeric_cols)
            
            # Correlações importantes
            correlations = self._analyze_correlations(df, numeric_cols)
            
            # Amostra dos dados
            sample = df.head(5).to_dict('records')
            
            # Gerar resumo executivo rico
            summary = self._generate_executive_summary(df, stats, trends, alerts, correlations)
            
            return {
                'type': 'csv',
                'filename': filename,
                'stats': stats,
                'sample': sample,
                'trends': trends,
                'alerts': alerts,
                'correlations': correlations,
                'summary': summary,
                'raw_data': df.to_dict('records') if len(df) <= 100 else None,
                'full_table': df.to_markdown() if len(df) <= 20 else None,
            }
        except Exception as e:
            return {
                'type': 'csv',
                'filename': filename,
                'error': str(e),
                'summary': f"Erro ao processar CSV: {str(e)}"
            }
    
    def _analyze_trends(self, df, numeric_cols: List[str]) -> Dict[str, Any]:
        """Analisa tendências nas colunas numéricas."""
        trends = {}
        
        if len(df) < 2:
            return trends
        
        for col in numeric_cols:
            try:
                values = df[col].dropna()
                if len(values) < 2:
                    continue
                
                first_value = values.iloc[0]
                last_value = values.iloc[-1]
                
                if first_value != 0:
                    change_pct = ((last_value - first_value) / abs(first_value)) * 100
                else:
                    change_pct = 0
                
                # Determinar direção e severidade
                if change_pct > 20:
                    direction = "📈 FORTE ALTA"
                elif change_pct > 5:
                    direction = "↗️ Alta"
                elif change_pct < -20:
                    direction = "📉 FORTE QUEDA"
                elif change_pct < -5:
                    direction = "↘️ Queda"
                else:
                    direction = "➡️ Estável"
                
                trends[col] = {
                    'first': first_value,
                    'last': last_value,
                    'change_pct': change_pct,
                    'direction': direction,
                    'min': values.min(),
                    'max': values.max(),
                    'mean': values.mean(),
                }
            except Exception:
                continue
        
        return trends
    
    def _detect_alerts(self, df, numeric_cols: List[str]) -> List[Dict]:
        """Detecta alertas e anomalias nos dados."""
        alerts = []
        
        if len(df) < 2:
            return alerts
        
        for col in numeric_cols:
            try:
                values = df[col].dropna()
                if len(values) < 2:
                    continue
                
                first_value = values.iloc[0]
                last_value = values.iloc[-1]
                change_pct = ((last_value - first_value) / abs(first_value)) * 100 if first_value != 0 else 0
                
                # Detectar variações significativas
                if abs(change_pct) > 30:
                    severity = "CRÍTICO" if abs(change_pct) > 50 else "ALERTA"
                    alerts.append({
                        'column': col,
                        'severity': severity,
                        'message': f"{col}: variação de {change_pct:+.1f}% ({first_value:.2f} → {last_value:.2f})",
                        'change_pct': change_pct,
                    })
                
                # Detectar valores em limite
                mean_val = values.mean()
                std_val = values.std()
                if std_val > 0 and abs(last_value - mean_val) > 2 * std_val:
                    alerts.append({
                        'column': col,
                        'severity': 'ATENÇÃO',
                        'message': f"{col}: último valor ({last_value:.2f}) está 2+ desvios padrão da média ({mean_val:.2f})",
                        'change_pct': change_pct,
                    })
            except Exception:
                continue
        
        return alerts
    
    def _analyze_correlations(self, df, numeric_cols: List[str]) -> List[Dict]:
        """Analisa correlações entre colunas numéricas."""
        correlations = []
        
        if len(numeric_cols) < 2 or len(df) < 3:
            return correlations
        
        try:
            corr_matrix = df[numeric_cols].corr()
            
            for i, col1 in enumerate(numeric_cols):
                for col2 in numeric_cols[i+1:]:
                    corr_value = corr_matrix.loc[col1, col2]
                    
                    if abs(corr_value) > 0.7:
                        relation = "positiva forte" if corr_value > 0 else "negativa forte"
                        correlations.append({
                            'columns': (col1, col2),
                            'correlation': corr_value,
                            'relation': relation,
                            'insight': f"{col1} e {col2} têm correlação {relation} ({corr_value:.2f})"
                        })
        except Exception:
            pass
        
        return correlations
    
    def _generate_executive_summary(self, df, stats: Dict, trends: Dict, alerts: List, correlations: List) -> str:
        """Gera resumo executivo rico para análise de negócios."""
        lines = [
            f"## 📊 Análise de Dados: {stats['rows']} registros",
            f"**Período**: {stats['rows']} períodos de dados",
            f"**Colunas analisadas**: {', '.join(stats['column_names'])}",
            ""
        ]
        
        # Alertas críticos primeiro
        if alerts:
            critical_alerts = [a for a in alerts if a['severity'] == 'CRÍTICO']
            warning_alerts = [a for a in alerts if a['severity'] == 'ALERTA']
            
            if critical_alerts:
                lines.append("### 🚨 ALERTAS CRÍTICOS")
                for alert in critical_alerts:
                    lines.append(f"- **{alert['message']}**")
                lines.append("")
            
            if warning_alerts:
                lines.append("### ⚠️ Alertas")
                for alert in warning_alerts:
                    lines.append(f"- {alert['message']}")
                lines.append("")
        
        # Tendências principais
        if trends:
            lines.append("### 📈 Tendências Identificadas")
            for col, trend in trends.items():
                lines.append(f"- **{col}**: {trend['direction']} ({trend['change_pct']:+.1f}%)")
                lines.append(f"  - Início: {trend['first']:.2f} → Atual: {trend['last']:.2f}")
                lines.append(f"  - Média: {trend['mean']:.2f} | Min: {trend['min']:.2f} | Max: {trend['max']:.2f}")
            lines.append("")
        
        # Correlações importantes
        if correlations:
            lines.append("### 🔗 Correlações Importantes")
            for corr in correlations:
                lines.append(f"- {corr['insight']}")
            lines.append("")
        
        # Tabela de dados completa (se pequena)
        if len(df) <= 12:
            lines.append("### 📋 Dados Completos")
            lines.append(df.to_markdown(index=False))
            lines.append("")
        else:
            # Mostrar primeira e última linha para contexto
            lines.append("### 📋 Amostra (primeiro e último período)")
            sample_df = df.iloc[[0, -1]]
            lines.append(sample_df.to_markdown(index=False))
            lines.append("")
        
        return "\n".join(lines)


class ExcelProcessor(FileProcessor):
    """Processa arquivos Excel."""
    
    def supports(self, filename: str) -> bool:
        return filename.lower().endswith(('.xlsx', '.xls'))
    
    def process(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extrai conteúdo de Excel."""
        try:
            import pandas as pd
            
            # Ler todas as sheets
            excel_file = pd.ExcelFile(io.BytesIO(file_content))
            sheets = {}
            
            for sheet_name in excel_file.sheet_names[:5]:  # Limitar a 5 sheets
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                sheets[sheet_name] = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'sample': df.head(5).to_dict('records'),
                }
            
            summary = self._generate_summary(sheets, filename)
            
            return {
                'type': 'excel',
                'filename': filename,
                'sheets': sheets,
                'sheet_names': excel_file.sheet_names,
                'summary': summary,
            }
        except Exception as e:
            return {
                'type': 'excel',
                'filename': filename,
                'error': str(e),
                'summary': f"Erro ao processar Excel: {str(e)}"
            }
    
    def _generate_summary(self, sheets: Dict, filename: str) -> str:
        """Gera resumo textual do Excel."""
        lines = [
            f"**Arquivo Excel**: {filename}",
            f"**Sheets**: {len(sheets)} planilhas",
        ]
        
        for sheet_name, info in sheets.items():
            lines.append(f"\n**{sheet_name}**: {info['rows']} linhas x {info['columns']} colunas")
            lines.append(f"  Colunas: {', '.join(info['column_names'][:5])}{'...' if len(info['column_names']) > 5 else ''}")
        
        return "\n".join(lines)


class PDFProcessor(FileProcessor):
    """Processa arquivos PDF."""
    
    def supports(self, filename: str) -> bool:
        return filename.lower().endswith('.pdf')
    
    def process(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extrai texto de PDF."""
        try:
            # Tentar usar PyPDF2
            try:
                import PyPDF2
                
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                text_pages = []
                
                for i, page in enumerate(pdf_reader.pages[:20]):  # Limitar a 20 páginas
                    text = page.extract_text()
                    if text:
                        text_pages.append({
                            'page': i + 1,
                            'text': text[:2000]  # Limitar texto por página
                        })
                
                full_text = "\n\n".join([p['text'] for p in text_pages])
                
                return {
                    'type': 'pdf',
                    'filename': filename,
                    'pages': len(pdf_reader.pages),
                    'text_pages': text_pages,
                    'summary': self._generate_summary(filename, len(pdf_reader.pages), full_text),
                    'full_text': full_text[:10000],  # Limitar texto total
                }
            except ImportError:
                # Fallback: apenas informar que PDF foi recebido
                return {
                    'type': 'pdf',
                    'filename': filename,
                    'summary': f"PDF recebido: {filename}. Instale PyPDF2 para extração de texto.",
                    'error': 'PyPDF2 não instalado'
                }
        except Exception as e:
            return {
                'type': 'pdf',
                'filename': filename,
                'error': str(e),
                'summary': f"Erro ao processar PDF: {str(e)}"
            }
    
    def _generate_summary(self, filename: str, pages: int, text: str) -> str:
        """Gera resumo textual do PDF."""
        # Primeiros 500 caracteres do texto
        preview = text[:500].replace('\n', ' ').strip()
        
        return f"**PDF**: {filename}\n**Páginas**: {pages}\n**Preview**:\n{preview}..."


class TextProcessor(FileProcessor):
    """Processa arquivos de texto."""
    
    def supports(self, filename: str) -> bool:
        return filename.lower().endswith(('.txt', '.md', '.json'))
    
    def process(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Extrai conteúdo de arquivo de texto."""
        try:
            text = file_content.decode('utf-8', errors='ignore')
            
            return {
                'type': 'text',
                'filename': filename,
                'content': text[:10000],  # Limitar tamanho
                'length': len(text),
                'summary': f"**Arquivo texto**: {filename}\n**Tamanho**: {len(text)} caracteres\n\n{text[:500]}..."
            }
        except Exception as e:
            return {
                'type': 'text',
                'filename': filename,
                'error': str(e),
                'summary': f"Erro ao processar texto: {str(e)}"
            }


# Lista de processadores disponíveis
PROCESSORS = [
    CSVProcessor(),
    ExcelProcessor(),
    PDFProcessor(),
    TextProcessor(),
]


def process_uploaded_file(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Processa arquivo uploaded e extrai conteúdo.
    
    Args:
        file_content: Conteúdo do arquivo em bytes
        filename: Nome do arquivo
    
    Returns:
        Dict com conteúdo extraído e metadados
    """
    for processor in PROCESSORS:
        if processor.supports(filename):
            return processor.process(file_content, filename)
    
    # Arquivo não suportado
    return {
        'type': 'unknown',
        'filename': filename,
        'summary': f"Tipo de arquivo não suportado: {filename}",
        'supported_types': ['CSV', 'Excel (xlsx, xls)', 'PDF', 'Texto (txt, md, json)']
    }


def format_files_context(processed_files: List[Dict]) -> str:
    """
    Formata arquivos processados para contexto dos agentes.
    
    Args:
        processed_files: Lista de arquivos processados
    
    Returns:
        String formatada para incluir no contexto
    """
    if not processed_files:
        return ""
    
    lines = [
        "\n\n" + "="*60,
        "# 📎 DADOS ANEXADOS PARA ANÁLISE",
        "="*60,
        "",
        "**IMPORTANTE**: Use os dados abaixo como base factual para sua análise.",
        "Priorize insights baseados em evidências dos dados fornecidos.",
        ""
    ]
    
    for i, file_data in enumerate(processed_files, 1):
        lines.append(f"\n## 📄 Arquivo {i}: {file_data.get('filename', 'Desconhecido')}")
        lines.append("-" * 40)
        
        # Resumo principal (já inclui alertas, tendências, etc.)
        lines.append(file_data.get('summary', 'Sem resumo disponível'))
        
        # Para CSVs, adicionar alertas de forma destacada
        if file_data.get('type') == 'csv':
            alerts = file_data.get('alerts', [])
            if alerts:
                lines.append("\n#### 🎯 PONTOS DE ATENÇÃO PARA ANÁLISE:")
                for alert in alerts:
                    lines.append(f"- [{alert['severity']}] {alert['message']}")
            
            # Adicionar correlações
            correlations = file_data.get('correlations', [])
            if correlations:
                lines.append("\n#### 🔗 RELAÇÕES ENTRE MÉTRICAS:")
                for corr in correlations:
                    lines.append(f"- {corr['insight']}")
            
            # Tabela completa se disponível
            if file_data.get('full_table'):
                lines.append("\n#### 📋 DADOS COMPLETOS:")
                lines.append(file_data['full_table'])
        
        if file_data.get('type') == 'pdf' and file_data.get('full_text'):
            lines.append(f"\n#### 📝 CONTEÚDO DO DOCUMENTO:")
            lines.append(file_data['full_text'][:3000])
        
        if file_data.get('type') == 'text' and file_data.get('content'):
            lines.append(f"\n#### 📝 CONTEÚDO:")
            lines.append(file_data['content'][:3000])
        
        lines.append("")
    
    lines.append("="*60)
    lines.append("FIM DOS DADOS ANEXADOS")
    lines.append("="*60)
    
    return "\n".join(lines)
