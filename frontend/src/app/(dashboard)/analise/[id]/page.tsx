'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { apiClient } from '@/services/api-client';
import { toast } from 'sonner';
import Link from 'next/link';
import {
  ArrowLeft,
  Loader2,
  CheckCircle2,
  Clock,
  XCircle,
  User,
  TrendingUp,
  DollarSign,
  Target,
  FileText,
  RefreshCw,
  Download,
  Share2,
  Briefcase,
  LineChart,
  Users,
  Lightbulb,
  Send,
  MessageSquare,
  FileDown,
  Presentation,
  FileType2,
  ChevronDown,
} from 'lucide-react';
import { MarkdownRenderer } from '@/components/ui/MarkdownRenderer';

interface AgentOutput {
  agent_name: string;
  output: string;
  status: string;
  latency_ms?: number;
}

interface Analysis {
  id: string;
  problem_description: string;
  business_type: string;
  analysis_depth: string;
  status: string;
  created_at: string;
  completed_at?: string;
  executive_summary?: string;
  agent_outputs?: AgentOutput[];
  results?: Record<string, string>;
}

const AGENT_INFO: Record<string, { icon: React.ElementType; label: string; color: string; bgColor: string; description: string; detailedDescription: string; deliverables: string[] }> = {
  analyst: { 
    icon: FileText, 
    label: 'Analista de Negócios', 
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    description: 'Análise detalhada do problema e contexto',
    detailedDescription: 'O Analista de Negócios examina profundamente o cenário apresentado, identificando padrões, causas raiz e variáveis críticas que impactam seu negócio.',
    deliverables: ['Síntese do problema', 'Hipóteses principais', 'Variáveis críticas', 'Próximos passos sugeridos']
  },
  commercial: { 
    icon: Target, 
    label: 'Especialista Comercial', 
    color: 'text-emerald-500',
    bgColor: 'bg-emerald-500/10',
    description: 'Estratégias de vendas e crescimento',
    detailedDescription: 'O Especialista Comercial transforma hipóteses em ações concretas, propondo estratégias de aquisição, retenção e expansão para impulsionar suas vendas.',
    deliverables: ['Estratégia geral', 'Ações de curto prazo', 'Ações de médio/longo prazo', 'Métricas de sucesso']
  },
  financial: { 
    icon: DollarSign, 
    label: 'Especialista Financeiro', 
    color: 'text-amber-500',
    bgColor: 'bg-amber-500/10',
    description: 'Análise financeira e projeções',
    detailedDescription: 'O Especialista Financeiro avalia a viabilidade das estratégias, estimando investimentos, retornos e riscos para garantir decisões financeiramente sólidas.',
    deliverables: ['Análise de viabilidade', 'Estimativa de investimento', 'Projeção de retorno', 'Priorização por ROI']
  },
  market: { 
    icon: TrendingUp, 
    label: 'Especialista de Mercado', 
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
    description: 'Tendências e análise competitiva',
    detailedDescription: 'O Especialista de Mercado valida hipóteses com base em tendências, benchmarks e padrões competitivos, contextualizando seu negócio no ecossistema.',
    deliverables: ['Contexto de mercado', 'Benchmarks relevantes', 'Riscos competitivos', 'Oportunidades identificadas']
  },
  reviewer: { 
    icon: Lightbulb, 
    label: 'Diagnóstico Executivo', 
    color: 'text-rose-500',
    bgColor: 'bg-rose-500/10',
    description: 'Síntese executiva e recomendações',
    detailedDescription: 'O Revisor Executivo consolida todas as análises, resolve contradições e entrega um plano de ação priorizado, pronto para apresentação ao board.',
    deliverables: ['Diagnóstico executivo', 'Recomendação estratégica', 'Plano de ação consolidado', 'Próximos passos imediatos']
  },
};

// Componente de Carrossel de Loading dos Agentes
function AgentLoadingCarousel() {
  const [activeAgentIndex, setActiveAgentIndex] = useState(0);
  const agents = Object.entries(AGENT_INFO);
  
  // Rotaciona automaticamente entre os agentes
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveAgentIndex((prev) => (prev + 1) % agents.length);
    }, 4000); // Muda a cada 4 segundos
    
    return () => clearInterval(interval);
  }, [agents.length]);
  
  const [activeKey, activeAgent] = agents[activeAgentIndex];
  const ActiveIcon = activeAgent.icon;
  
  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl p-8 mb-6 overflow-hidden relative">
      {/* Background Animation */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-primary/20 to-transparent rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-blue-500/20 to-transparent rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>
      
      <div className="relative z-10">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full mb-4">
            <Loader2 className="w-4 h-4 text-primary animate-spin" />
            <span className="text-sm font-medium text-white">Análise em andamento</span>
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">
            🤖 Time de Especialistas Trabalhando
          </h2>
          <p className="text-gray-400">
            5 agentes de IA estão analisando seu problema simultaneamente
          </p>
        </div>
        
        {/* Agent Selector Pills */}
        <div className="flex justify-center gap-2 mb-8">
          {agents.map(([key, agent], index) => {
            const Icon = agent.icon;
            const isActive = index === activeAgentIndex;
            return (
              <button
                key={key}
                onClick={() => setActiveAgentIndex(index)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-300 ${
                  isActive 
                    ? 'bg-white text-gray-900 shadow-lg shadow-white/20 scale-105' 
                    : 'bg-white/10 text-gray-400 hover:bg-white/20'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm font-medium hidden sm:inline">
                  {agent.label.split(' ').slice(-1)[0]}
                </span>
              </button>
            );
          })}
        </div>
        
        {/* Active Agent Card */}
        <div className="max-w-2xl mx-auto">
          <div 
            key={activeKey}
            className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 animate-fadeIn"
          >
            <div className="flex items-start gap-4">
              {/* Agent Icon */}
              <div className={`w-16 h-16 rounded-2xl ${activeAgent.bgColor} flex items-center justify-center flex-shrink-0`}>
                <ActiveIcon className={`w-8 h-8 ${activeAgent.color}`} />
              </div>
              
              {/* Agent Info */}
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-xl font-bold text-white">{activeAgent.label}</h3>
                  <span className="flex items-center gap-1 px-2 py-0.5 bg-primary/20 rounded-full">
                    <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                    <span className="text-xs text-primary font-medium">Analisando</span>
                  </span>
                </div>
                <p className="text-gray-300 mb-4">
                  {activeAgent.detailedDescription}
                </p>
                
                {/* Deliverables */}
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-400">O que este agente vai entregar:</p>
                  <div className="grid grid-cols-2 gap-2">
                    {activeAgent.deliverables.map((item, idx) => (
                      <div 
                        key={idx}
                        className="flex items-center gap-2 text-sm text-gray-300"
                        style={{ animationDelay: `${idx * 0.1}s` }}
                      >
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Progress Indicator */}
        <div className="mt-8 flex flex-col items-center">
          <div className="flex items-center gap-1 mb-2">
            {agents.map((_, index) => (
              <div 
                key={index}
                className={`h-1 rounded-full transition-all duration-300 ${
                  index === activeAgentIndex 
                    ? 'w-8 bg-primary' 
                    : 'w-2 bg-white/20'
                }`}
              />
            ))}
          </div>
          <p className="text-sm text-gray-500">
            ⏱️ Tempo estimado: 30-60 segundos
          </p>
        </div>
      </div>
    </div>
  );
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

// Componente de Exportação
function ExportDropdown({ analysisId }: { analysisId: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isExporting, setIsExporting] = useState<string | null>(null);

  const exportFormats = [
    { key: 'pdf', label: 'PDF', icon: FileDown, description: 'Relatório completo' },
    { key: 'pptx', label: 'PowerPoint', icon: Presentation, description: 'Apresentação executiva' },
    { key: 'docx', label: 'Word', icon: FileType2, description: 'Documento editável' },
  ];

  const handleExport = async (format: string) => {
    setIsExporting(format);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/async/analyses/${analysisId}/export/${format}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${document.cookie.split('access_token=')[1]?.split(';')[0] || ''}`,
        },
      });

      if (!response.ok) {
        throw new Error('Erro ao exportar');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analise-${analysisId}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success(`Relatório ${format.toUpperCase()} baixado com sucesso!`);
    } catch (error) {
      toast.error(`Erro ao exportar ${format.toUpperCase()}`);
    } finally {
      setIsExporting(null);
      setIsOpen(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
      >
        <Download className="w-4 h-4" />
        Exportar
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      
      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)} 
          />
          <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-20">
            {exportFormats.map((format) => {
              const Icon = format.icon;
              const isLoading = isExporting === format.key;
              return (
                <button
                  key={format.key}
                  onClick={() => handleExport(format.key)}
                  disabled={isExporting !== null}
                  className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 text-primary animate-spin" />
                  ) : (
                    <Icon className="w-5 h-5 text-gray-500" />
                  )}
                  <div className="text-left">
                    <p className="font-medium text-gray-900 dark:text-white text-sm">
                      {format.label}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {format.description}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

export default function AnalisePage() {
  const params = useParams();
  const router = useRouter();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('executive');
  const [isPolling, setIsPolling] = useState(false);
  const [previousStatus, setPreviousStatus] = useState<string | null>(null);
  const [showCompletedAnimation, setShowCompletedAnimation] = useState(false);
  
  // Chat de refino
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [refineUsage, setRefineUsage] = useState<{ used: number; limit: number; remaining: number } | null>(null);
  const [refineLimitReached, setRefineLimitReached] = useState(false);

  const sendChatMessage = async () => {
    if (!chatInput.trim() || isSendingMessage) return;
    
    const userMessage: ChatMessage = {
      role: 'user',
      content: chatInput.trim(),
      timestamp: new Date(),
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setIsSendingMessage(true);
    
    try {
      // Chama API de refino
      const response = await apiClient.post('/async/analyses/refine', {
        analysis_id: params.id,
        message: userMessage.content,
        context: analysis?.results || {},
      });
      
      const data = response.data as { 
        response: string; 
        usage?: { used: number; limit: number; remaining: number } 
      };
      
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.response || 'Desculpe, não consegui processar sua pergunta.',
        timestamp: new Date(),
      };
      
      setChatMessages(prev => [...prev, assistantMessage]);
      
      // Atualiza informações de uso
      if (data.usage) {
        setRefineUsage(data.usage);
        if (data.usage.remaining === 0) {
          setRefineLimitReached(true);
        }
      }
    } catch (error: any) {
      // Verifica se é erro de limite atingido (402)
      if (error.response?.status === 402) {
        const detail = error.response.data?.detail;
        setRefineLimitReached(true);
        if (detail?.used !== undefined) {
          setRefineUsage({ used: detail.used, limit: detail.limit, remaining: 0 });
        }
        toast.error(detail?.message || 'Limite de perguntas atingido. Faça upgrade do seu plano!');
      } else {
        toast.error('Erro ao enviar mensagem. Tente novamente.');
      }
      // Remove a mensagem do usuário se houver erro
      setChatMessages(prev => prev.slice(0, -1));
      setChatInput(userMessage.content);
    } finally {
      setIsSendingMessage(false);
    }
  };

  const loadAnalysis = useCallback(async () => {
    try {
      const data = await apiClient.getAnalysis(params.id as string);
      
      // Detecta transição de status para animação
      if (previousStatus && previousStatus !== data.status) {
        if (data.status === 'completed') {
          setShowCompletedAnimation(true);
          toast.success('✅ Análise concluída! Os resultados estão prontos.');
          setTimeout(() => setShowCompletedAnimation(false), 3000);
        } else if (data.status === 'running' && previousStatus === 'pending') {
          toast.info('🔄 Agentes iniciaram o processamento...');
        }
      }
      
      setPreviousStatus(data.status);
      setAnalysis(data);

      // Se ainda está processando, continua polling
      if (data.status === 'pending' || data.status === 'running') {
        setIsPolling(true);
      } else {
        setIsPolling(false);
      }
    } catch (error) {
      toast.error('Erro ao carregar análise');
      router.push('/dashboard');
    } finally {
      setIsLoading(false);
    }
  }, [params.id, router, previousStatus]);

  useEffect(() => {
    loadAnalysis();
  }, [loadAnalysis]);

  // Polling enquanto processa
  useEffect(() => {
    if (!isPolling) return;

    const interval = setInterval(() => {
      loadAnalysis();
    }, 3000);

    return () => clearInterval(interval);
  }, [isPolling, loadAnalysis]);

  const getStatusBadge = (status: string) => {
    const styles: Record<string, { bg: string; text: string; icon: React.ElementType }> = {
      pending: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-700 dark:text-yellow-400', icon: Clock },
      running: { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-400', icon: Loader2 },
      completed: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-400', icon: CheckCircle2 },
      failed: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400', icon: XCircle },
    };

    const style = styles[status] || styles.pending;
    const Icon = style.icon;
    const isSpinning = status === 'running';

    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${style.bg} ${style.text}`}>
        <Icon className={`w-4 h-4 ${isSpinning ? 'animate-spin' : ''}`} />
        {status === 'pending' && 'Aguardando'}
        {status === 'running' && 'Processando'}
        {status === 'completed' && 'Concluída'}
        {status === 'failed' && 'Falhou'}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Carregando análise...</p>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return null;
  }

  // Suporta tanto agent_outputs (objeto) quanto results (legado)
  const agentOutputs = (analysis as any).agent_outputs || {};
  const agentResults = analysis.results || {};
  
  // Converter agent_outputs para formato simples se necessário
  const getAgentContent = (agentKey: string): string => {
    // Tenta agent_outputs primeiro (novo formato)
    if (agentOutputs[agentKey]) {
      const output = agentOutputs[agentKey];
      return typeof output === 'string' ? output : output.content || output.output || '';
    }
    // Fallback para results (formato legado)
    return agentResults[agentKey] || '';
  };
  
  const hasResults = Object.keys(agentOutputs).length > 0 || Object.keys(agentResults).length > 0;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Dashboard
            </Link>

            <div className="flex items-center gap-3">
              {getStatusBadge(analysis.status)}
              
              {analysis.status === 'completed' && (
                <ExportDropdown analysisId={analysis.id} />
              )}

              {(analysis.status === 'pending' || analysis.status === 'running') && (
                <button
                  onClick={loadAnalysis}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <RefreshCw className={`w-5 h-5 ${isPolling ? 'animate-spin' : ''}`} />
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Problem Summary - Pergunta Completa */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 mb-6 overflow-hidden">
          <div className="px-6 py-4 bg-gradient-to-r from-primary/5 to-blue-500/5 border-b border-gray-100 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" />
              <span className="font-semibold text-gray-900 dark:text-white">Problema Analisado</span>
            </div>
          </div>
          <div className="p-6">
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="px-2.5 py-1 text-xs font-medium bg-primary/10 text-primary rounded-full">
                {analysis.business_type}
              </span>
              <span className="px-2.5 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full">
                {analysis.analysis_depth}
              </span>
              <span className="text-xs text-gray-400 dark:text-gray-500">
                • Criada em {new Date(analysis.created_at).toLocaleDateString('pt-BR', {
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>
            <p className="text-gray-800 dark:text-gray-200 leading-relaxed text-base">
              {analysis.problem_description}
            </p>
          </div>
        </div>

        {/* Processing State - Pending */}
        {analysis.status === 'pending' && (
          <div className="bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/20 rounded-2xl p-8 mb-6">
            <div className="flex flex-col items-center text-center">
              <div className="relative">
                <div className="absolute inset-0 bg-yellow-500/20 rounded-full blur-xl animate-pulse" />
                <div className="relative w-20 h-20 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center mb-4">
                  <Clock className="w-10 h-10 text-white" />
                </div>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                📋 Análise na Fila
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Sua análise está aguardando para ser processada...
              </p>
              <div className="flex items-center gap-2 text-sm text-yellow-600 dark:text-yellow-400">
                <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse" />
                Aguardando início
              </div>
            </div>
          </div>
        )}

        {/* Processing State - Running with Agent Carousel */}
        {analysis.status === 'running' && (
          <AgentLoadingCarousel />
        )}

        {/* Completed Animation */}
        {showCompletedAnimation && (
          <div className="bg-gradient-to-r from-emerald-500/10 to-green-500/10 border border-emerald-500/30 rounded-2xl p-6 mb-6 animate-fadeIn">
            <div className="flex items-center justify-center gap-3">
              <div className="w-12 h-12 rounded-full bg-emerald-500 flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-emerald-700 dark:text-emerald-400">
                  ✅ Análise Concluída!
                </h3>
                <p className="text-sm text-emerald-600 dark:text-emerald-500">
                  Todos os agentes finalizaram. Confira os resultados abaixo.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {analysis.status === 'completed' && hasResults && (
          <>
            {/* Agent Cards as Tabs */}
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-6">
              {/* Executive Summary Tab */}
              <button
                onClick={() => setActiveTab('executive')}
                className={`group relative p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                  activeTab === 'executive'
                    ? 'border-primary bg-primary/5 shadow-lg shadow-primary/10'
                    : 'border-gray-200 dark:border-gray-700 hover:border-primary/50 bg-white dark:bg-gray-800'
                }`}
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${
                  activeTab === 'executive' ? 'bg-primary/20' : 'bg-rose-500/10'
                }`}>
                  <Lightbulb className={`w-5 h-5 ${
                    activeTab === 'executive' ? 'text-primary' : 'text-rose-500'
                  }`} />
                </div>
                <p className={`font-medium text-sm ${
                  activeTab === 'executive' ? 'text-primary' : 'text-gray-900 dark:text-white'
                }`}>
                  Diagnóstico Executivo
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 hidden lg:block">
                  Síntese e recomendações
                </p>
                {activeTab === 'executive' && (
                  <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary animate-pulse" />
                )}
              </button>

              {/* Agent Tabs */}
              {Object.entries(AGENT_INFO).map(([key, info]) => {
                if (key === 'reviewer') return null;
                const Icon = info.icon;
                const isActive = activeTab === key;
                
                return (
                  <button
                    key={key}
                    onClick={() => setActiveTab(key)}
                    className={`group relative p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                      isActive
                        ? 'border-primary bg-primary/5 shadow-lg shadow-primary/10'
                        : 'border-gray-200 dark:border-gray-700 hover:border-primary/50 bg-white dark:bg-gray-800'
                    }`}
                  >
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${
                      isActive ? 'bg-primary/20' : info.bgColor
                    }`}>
                      <Icon className={`w-5 h-5 ${
                        isActive ? 'text-primary' : info.color
                      }`} />
                    </div>
                    <p className={`font-medium text-sm ${
                      isActive ? 'text-primary' : 'text-gray-900 dark:text-white'
                    }`}>
                      {info.label.split(' ').slice(-1)[0]}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 hidden lg:block truncate">
                      {info.description.slice(0, 25)}...
                    </p>
                    {isActive && (
                      <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary animate-pulse" />
                    )}
                  </button>
                );
              })}
            </div>

            {/* Content Card */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
              {/* Content Header */}
              <div className="px-6 py-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50">
                <div className="flex items-center gap-3">
                  {(() => {
                    const currentAgent = activeTab === 'executive' ? 'reviewer' : activeTab;
                    const info = AGENT_INFO[currentAgent];
                    const Icon = info?.icon || Lightbulb;
                    return (
                      <>
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${info?.bgColor || 'bg-primary/10'}`}>
                          <Icon className={`w-4 h-4 ${info?.color || 'text-primary'}`} />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white">
                            {info?.label || 'Diagnóstico Executivo'}
                          </h3>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {info?.description || 'Síntese executiva e recomendações'}
                          </p>
                        </div>
                      </>
                    );
                  })()}
                </div>
              </div>

              {/* Content Body */}
              <div className="p-6 lg:p-8">
                {activeTab === 'executive' && getAgentContent('reviewer') && (
                  <MarkdownRenderer content={getAgentContent('reviewer')} />
                )}

                {activeTab !== 'executive' && getAgentContent(activeTab) && (
                  <MarkdownRenderer content={getAgentContent(activeTab)} />
                )}

                {!getAgentContent(activeTab === 'executive' ? 'reviewer' : activeTab) && (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center mx-auto mb-4">
                      <FileText className="w-8 h-8 text-gray-400" />
                    </div>
                    <p className="text-gray-500 dark:text-gray-400">
                      Resultado não disponível para este agente.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Chat de Refino */}
            <div className="mt-6 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
              <button
                onClick={() => setShowChat(!showChat)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                    <MessageSquare className="w-5 h-5 text-primary" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      Refinar Análise
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Continue a conversa para aprofundar ou esclarecer pontos
                    </p>
                  </div>
                </div>
                <div className={`transform transition-transform ${showChat ? 'rotate-180' : ''}`}>
                  <ArrowLeft className="w-5 h-5 text-gray-400 -rotate-90" />
                </div>
              </button>
              
              {showChat && (
                <div className="border-t border-gray-100 dark:border-gray-700">
                  {/* Chat Messages */}
                  <div className="max-h-96 overflow-y-auto p-4 space-y-4">
                    {chatMessages.length === 0 && (
                      <div className="text-center py-8">
                        <MessageSquare className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                        <p className="text-gray-500 dark:text-gray-400 text-sm">
                          Faça perguntas para aprofundar a análise
                        </p>
                        <div className="flex flex-wrap justify-center gap-2 mt-4">
                          {[
                            'Pode detalhar mais as ações de curto prazo?',
                            'Quais são os riscos dessa estratégia?',
                            'Como medir o sucesso dessas ações?',
                          ].map((suggestion, idx) => (
                            <button
                              key={idx}
                              onClick={() => setChatInput(suggestion)}
                              className="px-3 py-1.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full hover:bg-primary/10 hover:text-primary transition-colors"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {chatMessages.map((msg, idx) => (
                      <div
                        key={idx}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                            msg.role === 'user'
                              ? 'bg-primary text-white rounded-br-md'
                              : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-md'
                          }`}
                        >
                          {msg.role === 'assistant' ? (
                            <MarkdownRenderer content={msg.content} />
                          ) : (
                            <p className="text-sm">{msg.content}</p>
                          )}
                          <p className={`text-xs mt-1 ${
                            msg.role === 'user' ? 'text-white/70' : 'text-gray-400'
                          }`}>
                            {msg.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      </div>
                    ))}
                    
                    {isSendingMessage && (
                      <div className="flex justify-start">
                        <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-md px-4 py-3">
                          <div className="flex items-center gap-2">
                            <Loader2 className="w-4 h-4 animate-spin text-primary" />
                            <span className="text-sm text-gray-500">Analisando...</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Chat Input */}
                  <div className="p-4 border-t border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50">
                    {/* Contador de uso */}
                    {refineUsage && refineUsage.limit !== -1 && (
                      <div className="flex items-center justify-between mb-3 text-xs">
                        <span className="text-gray-500 dark:text-gray-400">
                          Perguntas: {refineUsage.used}/{refineUsage.limit}
                        </span>
                        <div className="flex-1 mx-3 h-1.5 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full transition-all ${
                              refineUsage.remaining === 0 ? 'bg-red-500' : 
                              refineUsage.remaining <= 1 ? 'bg-yellow-500' : 'bg-primary'
                            }`}
                            style={{ width: `${(refineUsage.used / refineUsage.limit) * 100}%` }}
                          />
                        </div>
                        <span className={`font-medium ${
                          refineUsage.remaining === 0 ? 'text-red-500' : 'text-gray-500'
                        }`}>
                          {refineUsage.remaining === 0 ? 'Limite atingido' : `${refineUsage.remaining} restantes`}
                        </span>
                      </div>
                    )}
                    
                    {/* Mensagem de upgrade quando limite atingido */}
                    {refineLimitReached ? (
                      <div className="bg-gradient-to-r from-primary/10 to-purple-500/10 border border-primary/20 rounded-xl p-4">
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                            <MessageSquare className="w-5 h-5 text-primary" />
                          </div>
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900 dark:text-white">
                              Limite de perguntas atingido
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              Faça upgrade do seu plano para continuar conversando com a IA sobre esta análise.
                            </p>
                            <Link
                              href="/billing"
                              className="inline-flex items-center gap-2 mt-3 px-4 py-2 bg-primary text-white text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors"
                            >
                              🚀 Fazer Upgrade
                            </Link>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={chatInput}
                          onChange={(e) => setChatInput(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                          placeholder="Faça uma pergunta sobre a análise..."
                          className="flex-1 px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                          disabled={isSendingMessage}
                        />
                        <button
                          onClick={sendChatMessage}
                          disabled={!chatInput.trim() || isSendingMessage}
                          className="px-4 py-3 bg-primary text-white rounded-xl hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                          <Send className="w-5 h-5" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {/* Failed State */}
        {analysis.status === 'failed' && (
          <div className="bg-red-50 dark:bg-red-900/20 rounded-xl p-8 text-center">
            <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Erro na análise
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Ocorreu um erro ao processar sua análise. Por favor, tente novamente.
            </p>
            <Link
              href="/nova-analise"
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
            >
              Criar nova análise
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}
