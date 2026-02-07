'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import { apiClient } from '@/services/api-client';
import { toast } from 'sonner';
import { 
  BarChart3, 
  Plus, 
  Clock, 
  CheckCircle2, 
  XCircle,
  Loader2,
  ArrowRight,
  Sparkles,
  TrendingUp,
  Calendar,
  Zap
} from 'lucide-react';

interface Analysis {
  id: string;
  problem_description: string;
  business_type: string;
  status: string;
  created_at: string;
  executive_summary?: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, completed: 0, pending: 0 });

  useEffect(() => {
    loadAnalyses();
  }, []);

  const loadAnalyses = async () => {
    try {
      const data = await apiClient.listAnalyses({ limit: 10 });
      setAnalyses(data.items);
      
      const completed = data.items.filter((a: Analysis) => a.status === 'completed').length;
      const pending = data.items.filter((a: Analysis) => a.status === 'pending' || a.status === 'running').length;
      
      setStats({ total: data.total, completed, pending });
    } catch (error) {
      toast.error('Erro ao carregar análises');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'running':
        return <Loader2 className="w-5 h-5 text-brand-500 animate-spin" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getStatusText = (status: string) => {
    const map: Record<string, string> = {
      pending: 'Aguardando',
      running: 'Processando',
      completed: 'Concluída',
      failed: 'Falhou',
    };
    return map[status] || status;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-950">
      <div className="p-6 lg:p-8 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-primary/10 text-primary rounded-full">
                {user?.organization?.plan?.toUpperCase() || 'FREE'}
              </span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Olá, {user?.name?.split(' ')[0] || 'Usuário'} 👋
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              {user?.organization?.name || 'Minha Empresa'} • Aqui está um resumo das suas análises
            </p>
          </div>
          <button
            onClick={() => router.push('/nova-analise')}
            className="flex items-center justify-center gap-2 px-5 py-3 bg-gradient-to-r from-primary to-blue-600 hover:from-primary/90 hover:to-blue-600/90 text-white rounded-xl transition-all shadow-lg shadow-primary/25 hover:shadow-primary/40 font-medium"
          >
            <Zap className="w-5 h-5" />
            Criar Nova Análise
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-6 mb-8">
          <div className="group bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Total de Análises</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3 text-green-500" />
                  <span className="text-green-500">+12%</span> vs mês anterior
                </p>
              </div>
              <div className="p-3 bg-gradient-to-br from-primary/10 to-blue-500/10 rounded-xl group-hover:scale-110 transition-transform">
                <BarChart3 className="w-6 h-6 text-primary" />
              </div>
            </div>
          </div>

          <div className="group bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-lg hover:shadow-emerald-500/5 transition-all duration-300">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Concluídas</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.completed}</p>
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                  {stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0}% taxa de conclusão
                </p>
              </div>
              <div className="p-3 bg-gradient-to-br from-emerald-500/10 to-green-500/10 rounded-xl group-hover:scale-110 transition-transform">
                <CheckCircle2 className="w-6 h-6 text-emerald-500" />
              </div>
            </div>
          </div>

          <div className="group bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-lg hover:shadow-amber-500/5 transition-all duration-300">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Em Processamento</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.pending}</p>
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-2 flex items-center gap-1">
                  <Loader2 className="w-3 h-3 animate-spin text-amber-500" />
                  Atualizando em tempo real
                </p>
              </div>
              <div className="p-3 bg-gradient-to-br from-amber-500/10 to-orange-500/10 rounded-xl group-hover:scale-110 transition-transform">
                <Clock className="w-6 h-6 text-amber-500" />
              </div>
            </div>
          </div>
        </div>

        {/* Recent Analyses */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
          <div className="p-6 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Análises Recentes</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">Suas últimas análises estratégicas</p>
            </div>
            {analyses.length > 0 && (
              <span className="px-2.5 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full">
                {analyses.length} análises
              </span>
            )}
          </div>

          {analyses.length === 0 ? (
            <div className="p-12 text-center">
              <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-primary/10 to-blue-500/10 flex items-center justify-center">
                <Sparkles className="w-10 h-10 text-primary" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Comece sua primeira análise
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-sm mx-auto">
                Nosso time de 5 agentes de IA irá analisar seu problema de negócios e fornecer insights acionáveis.
              </p>
              <button
                onClick={() => router.push('/nova-analise')}
                className="inline-flex items-center gap-2 px-5 py-3 bg-gradient-to-r from-primary to-blue-600 hover:from-primary/90 hover:to-blue-600/90 text-white rounded-xl font-medium transition-all shadow-lg shadow-primary/25"
              >
                <Zap className="w-5 h-5" />
                Criar Primeira Análise
              </button>
            </div>
          ) : (
            <div className="divide-y divide-gray-100 dark:divide-gray-700">
              {analyses.map((analysis, index) => (
                <div
                  key={analysis.id}
                  onClick={() => router.push(`/analise/${analysis.id}`)}
                  className="p-5 hover:bg-gray-50/50 dark:hover:bg-gray-700/30 cursor-pointer transition-all group"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <div className="flex items-start gap-4">
                    <div className={`p-2.5 rounded-xl flex-shrink-0 ${
                      analysis.status === 'completed' ? 'bg-emerald-500/10' :
                      analysis.status === 'running' ? 'bg-primary/10' :
                      analysis.status === 'failed' ? 'bg-red-500/10' : 'bg-amber-500/10'
                    }`}>
                      {getStatusIcon(analysis.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className={`px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider rounded-full ${
                          analysis.status === 'completed' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' :
                          analysis.status === 'running' ? 'bg-primary/10 text-primary' :
                          analysis.status === 'failed' ? 'bg-red-500/10 text-red-600 dark:text-red-400' : 'bg-amber-500/10 text-amber-600 dark:text-amber-400'
                        }`}>
                          {getStatusText(analysis.status)}
                        </span>
                        <span className="px-2 py-0.5 text-[10px] font-medium bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 rounded-full">
                          {analysis.business_type}
                        </span>
                      </div>
                      <p className="text-gray-900 dark:text-white font-medium line-clamp-2 group-hover:text-primary transition-colors">
                        {analysis.problem_description.slice(0, 120)}...
                      </p>
                      <div className="flex items-center gap-2 mt-2 text-xs text-gray-400 dark:text-gray-500">
                        <Calendar className="w-3.5 h-3.5" />
                        {new Date(analysis.created_at).toLocaleDateString('pt-BR', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </div>
                    </div>
                    <ArrowRight className="w-5 h-5 text-gray-300 dark:text-gray-600 flex-shrink-0 group-hover:text-primary group-hover:translate-x-1 transition-all" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
