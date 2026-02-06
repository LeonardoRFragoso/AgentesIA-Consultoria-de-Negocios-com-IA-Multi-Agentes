"""
Modelo de dados para artefatos executivos profissionais.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class ExecutiveFormat(str, Enum):
    """Formatos de exportação executiva"""
    ONE_PAGER = "one_pager"      # Markdown, 1 página
    PDF = "pdf"                  # PDF formal
    PPT = "ppt"                  # PowerPoint estruturado
    JSON = "json"                # JSON estruturado


@dataclass
class ExecutiveAction:
    """Ação executiva com responsável e prazo"""
    description: str             # O que fazer
    owner: str                   # Quem é responsável
    due_date: Optional[str] = None  # Quando (ex: "5 dias úteis")
    priority: str = "normal"     # normal, high, critical


@dataclass
class ExecutiveRisk:
    """Risco identificado com mitigação"""
    risk: str                    # Qual é o risco
    probability: str             # Probabilidade (low, medium, high)
    impact: str                  # Impacto (low, medium, high, critical)
    mitigation: Optional[str] = None  # Como mitigar


@dataclass
class ExecutiveSummary:
    """Resumo executivo para C-Level"""
    
    # Identificação (sem valores padrão)
    execution_id: str
    title: str                   # Título da decisão
    
    # Conteúdo principal (sem valores padrão)
    context: str                 # Contexto em 2-3 frases
    key_decision: str            # Decisão em 1 frase
    rationale: str               # Por que em 3-4 frases
    confidence_score: float      # 0.0 a 1.0
    
    # Metadados com valores padrão
    date: datetime = field(default_factory=datetime.now)
    risks: List[ExecutiveRisk] = field(default_factory=list)
    action_items: List[ExecutiveAction] = field(default_factory=list)
    owner: str = "CEO"           # Quem é responsável
    review_date: Optional[str] = None  # Quando revisar (ex: "30 dias")
    
    # Opcional: contexto técnico
    business_type: Optional[str] = None
    analysis_depth: Optional[str] = None
    
    # Opcional: alternativas consideradas
    alternatives_considered: List[str] = field(default_factory=list)
    
    # Opcional: métricas de sucesso
    success_metrics: List[str] = field(default_factory=list)
    
    def to_one_pager(self) -> str:
        """Exporta como one-pager em Markdown"""
        lines = []
        
        # Cabeçalho
        lines.append(f"# {self.title}")
        lines.append(f"**Data**: {self.date.strftime('%d/%m/%Y')}")
        lines.append(f"**Responsável**: {self.owner}")
        lines.append("")
        
        # Contexto
        lines.append("## CONTEXTO")
        lines.append(self.context)
        lines.append("")
        
        # Decisão
        lines.append("## DECISÃO")
        lines.append(f"**{self.key_decision}**")
        lines.append("")
        
        # Rationale
        lines.append("## RATIONALE")
        lines.append(self.rationale)
        lines.append(f"**Confiança**: {self.confidence_score:.0%}")
        lines.append("")
        
        # Ações
        if self.action_items:
            lines.append("## AÇÕES IMEDIATAS")
            for action in self.action_items:
                lines.append(f"- **{action.description}**")
                lines.append(f"  - Responsável: {action.owner}")
                if action.due_date:
                    lines.append(f"  - Prazo: {action.due_date}")
            lines.append("")
        
        # Riscos
        if self.risks:
            lines.append("## RISCOS")
            for risk in self.risks:
                lines.append(f"- **{risk.risk}**")
                lines.append(f"  - Probabilidade: {risk.probability}")
                lines.append(f"  - Impacto: {risk.impact}")
                if risk.mitigation:
                    lines.append(f"  - Mitigação: {risk.mitigation}")
            lines.append("")
        
        # Revisão
        if self.review_date:
            lines.append("## PRÓXIMOS PASSOS")
            lines.append(f"- Revisar em {self.review_date}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Exporta como dicionário estruturado"""
        return {
            "execution_id": self.execution_id,
            "title": self.title,
            "date": self.date.isoformat(),
            "context": self.context,
            "key_decision": self.key_decision,
            "rationale": self.rationale,
            "confidence_score": self.confidence_score,
            "owner": self.owner,
            "review_date": self.review_date,
            "risks": [
                {
                    "risk": r.risk,
                    "probability": r.probability,
                    "impact": r.impact,
                    "mitigation": r.mitigation
                }
                for r in self.risks
            ],
            "action_items": [
                {
                    "description": a.description,
                    "owner": a.owner,
                    "due_date": a.due_date,
                    "priority": a.priority
                }
                for a in self.action_items
            ],
            "alternatives_considered": self.alternatives_considered,
            "success_metrics": self.success_metrics
        }
    
    def __repr__(self) -> str:
        return (
            f"ExecutiveSummary("
            f"title='{self.title}', "
            f"confidence={self.confidence_score:.0%}, "
            f"actions={len(self.action_items)}"
            f")"
        )


@dataclass
class ExecutiveReport:
    """Relatório executivo completo (PDF/PPT)"""
    
    summary: ExecutiveSummary
    
    # Seções adicionais
    executive_summary_text: str  # Parágrafo de 1-2 linhas
    background: str              # Contexto detalhado (3-4 parágrafos)
    analysis_summary: str        # Resumo da análise (2-3 parágrafos)
    
    # Alternativas
    alternatives: List[Dict] = field(default_factory=list)  # {name, pros, cons}
    
    # Implementação
    implementation_plan: List[str] = field(default_factory=list)
    timeline: Optional[str] = None
    
    # Métricas
    expected_outcomes: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    
    # Aprovações
    approvals_required: List[str] = field(default_factory=list)
    
    def get_pdf_structure(self) -> Dict:
        """Retorna estrutura para PDF"""
        return {
            "cover": {
                "title": self.summary.title,
                "date": self.summary.date.strftime("%d/%m/%Y"),
                "owner": self.summary.owner
            },
            "executive_summary": self.executive_summary_text,
            "background": self.background,
            "decision": self.summary.key_decision,
            "rationale": self.summary.rationale,
            "analysis": self.analysis_summary,
            "alternatives": self.alternatives,
            "implementation": self.implementation_plan,
            "timeline": self.timeline,
            "risks": [
                {
                    "risk": r.risk,
                    "probability": r.probability,
                    "impact": r.impact,
                    "mitigation": r.mitigation
                }
                for r in self.summary.risks
            ],
            "actions": [
                {
                    "description": a.description,
                    "owner": a.owner,
                    "due_date": a.due_date
                }
                for a in self.summary.action_items
            ],
            "success_criteria": self.success_criteria,
            "approvals": self.approvals_required
        }
    
    def get_ppt_structure(self) -> List[Dict]:
        """Retorna estrutura para PowerPoint"""
        slides = []
        
        # Slide 1: Capa
        slides.append({
            "title": self.summary.title,
            "subtitle": self.summary.date.strftime("%d/%m/%Y"),
            "content": f"Responsável: {self.summary.owner}",
            "type": "cover"
        })
        
        # Slide 2: Contexto
        slides.append({
            "title": "CONTEXTO",
            "content": self.background,
            "type": "text"
        })
        
        # Slide 3: Decisão
        slides.append({
            "title": "DECISÃO",
            "content": self.summary.key_decision,
            "subtitle": f"Confiança: {self.summary.confidence_score:.0%}",
            "type": "highlight"
        })
        
        # Slide 4: Rationale
        slides.append({
            "title": "RATIONALE",
            "content": self.summary.rationale,
            "type": "text"
        })
        
        # Slide 5: Alternativas
        if self.alternatives:
            slides.append({
                "title": "ALTERNATIVAS CONSIDERADAS",
                "content": self.alternatives,
                "type": "list"
            })
        
        # Slide 6: Plano de Ação
        slides.append({
            "title": "PLANO DE AÇÃO",
            "content": [
                f"{a.description} ({a.owner}, {a.due_date})"
                for a in self.summary.action_items
            ],
            "type": "list"
        })
        
        # Slide 7: Riscos
        if self.summary.risks:
            slides.append({
                "title": "RISCOS E MITIGAÇÃO",
                "content": [
                    f"{r.risk} ({r.probability}/{r.impact})"
                    for r in self.summary.risks
                ],
                "type": "list"
            })
        
        # Slide 8: Próximos Passos
        slides.append({
            "title": "PRÓXIMOS PASSOS",
            "content": [
                f"Revisar em {self.summary.review_date}" if self.summary.review_date else "Monitorar implementação"
            ],
            "type": "list"
        })
        
        return slides
