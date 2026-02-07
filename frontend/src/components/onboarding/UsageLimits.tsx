'use client';

import { useAuthStore } from '@/stores/auth-store';
import { AlertTriangle, Zap, TrendingUp, Crown } from 'lucide-react';

interface PlanLimits {
  analysesPerMonth: number;
  analysesUsed: number;
  agentsAvailable: number;
  exportFormats: string[];
  priority: string;
}

interface UsageLimitsProps {
  limits?: PlanLimits;
  onUpgrade?: () => void;
}

const PLAN_LIMITS: Record<string, PlanLimits> = {
  free: {
    analysesPerMonth: 3,
    analysesUsed: 0,
    agentsAvailable: 3,
    exportFormats: ['PDF'],
    priority: 'Normal',
  },
  starter: {
    analysesPerMonth: 20,
    analysesUsed: 0,
    agentsAvailable: 5,
    exportFormats: ['PDF', 'DOCX'],
    priority: 'Média',
  },
  professional: {
    analysesPerMonth: 100,
    analysesUsed: 0,
    agentsAvailable: 5,
    exportFormats: ['PDF', 'DOCX', 'Excel'],
    priority: 'Alta',
  },
  enterprise: {
    analysesPerMonth: -1, // Ilimitado
    analysesUsed: 0,
    agentsAvailable: 5,
    exportFormats: ['PDF', 'DOCX', 'Excel', 'API'],
    priority: 'Máxima',
  },
};

export function UsageLimits({ limits, onUpgrade }: UsageLimitsProps) {
  const { user } = useAuthStore();
  const plan = user?.organization?.plan || 'free';
  const planLimits = limits || PLAN_LIMITS[plan] || PLAN_LIMITS.free;
  
  const usagePercent = planLimits.analysesPerMonth > 0 
    ? (planLimits.analysesUsed / planLimits.analysesPerMonth) * 100 
    : 0;
  const isNearLimit = usagePercent >= 80;
  const isAtLimit = usagePercent >= 100;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900 dark:text-white">
          Uso do Plano
        </h3>
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
          plan === 'free' 
            ? 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
            : 'bg-brand-100 text-brand-600 dark:bg-brand-900/30'
        }`}>
          {plan.toUpperCase()}
        </span>
      </div>

      {/* Progress bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-gray-600 dark:text-gray-400">
            Análises este mês
          </span>
          <span className={`font-medium ${
            isAtLimit ? 'text-red-500' : isNearLimit ? 'text-yellow-500' : 'text-gray-900 dark:text-white'
          }`}>
            {planLimits.analysesUsed} / {planLimits.analysesPerMonth === -1 ? '∞' : planLimits.analysesPerMonth}
          </span>
        </div>
        <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div 
            className={`h-full transition-all duration-500 ${
              isAtLimit ? 'bg-red-500' : isNearLimit ? 'bg-yellow-500' : 'bg-brand-500'
            }`}
            style={{ width: `${Math.min(usagePercent, 100)}%` }}
          />
        </div>
      </div>

      {/* Warning if near/at limit */}
      {isNearLimit && plan === 'free' && (
        <div className={`p-3 rounded-lg mb-4 ${
          isAtLimit 
            ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800' 
            : 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800'
        }`}>
          <div className="flex items-start gap-3">
            <AlertTriangle className={`w-5 h-5 flex-shrink-0 ${
              isAtLimit ? 'text-red-500' : 'text-yellow-500'
            }`} />
            <div>
              <p className={`text-sm font-medium ${
                isAtLimit ? 'text-red-700 dark:text-red-400' : 'text-yellow-700 dark:text-yellow-400'
              }`}>
                {isAtLimit 
                  ? 'Limite atingido!' 
                  : 'Você está quase no limite'
                }
              </p>
              <p className={`text-xs ${
                isAtLimit ? 'text-red-600 dark:text-red-500' : 'text-yellow-600 dark:text-yellow-500'
              }`}>
                {isAtLimit 
                  ? 'Faça upgrade para continuar criando análises.' 
                  : 'Considere fazer upgrade para mais análises.'
                }
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Plan features */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Agentes IA</span>
          <span className="text-gray-900 dark:text-white">
            {planLimits.agentsAvailable} de 5
          </span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Exportação</span>
          <span className="text-gray-900 dark:text-white">
            {planLimits.exportFormats.join(', ')}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Prioridade</span>
          <span className="text-gray-900 dark:text-white">
            {planLimits.priority}
          </span>
        </div>
      </div>

      {/* Upgrade CTA for free plan */}
      {plan === 'free' && (
        <button
          onClick={onUpgrade}
          className="w-full flex items-center justify-center gap-2 py-2 px-4 bg-gradient-to-r from-brand-500 to-purple-500 hover:from-brand-600 hover:to-purple-600 text-white font-medium rounded-lg transition-all"
        >
          <Zap className="w-4 h-4" />
          Fazer Upgrade
        </button>
      )}
    </div>
  );
}

// Componente para mostrar o que o usuário ganha com upgrade
export function UpgradeComparison({ onUpgrade }: { onUpgrade?: () => void }) {
  return (
    <div className="bg-gradient-to-br from-brand-50 to-purple-50 dark:from-brand-900/20 dark:to-purple-900/20 rounded-2xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-brand-500 rounded-xl flex items-center justify-center">
          <Crown className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="font-semibold text-gray-900 dark:text-white">
            Desbloqueie todo o potencial
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Com o plano Starter
          </p>
        </div>
      </div>

      <ul className="space-y-3 mb-6">
        {[
          { icon: TrendingUp, text: '20 análises/mês (vs 3)' },
          { icon: Zap, text: 'Todos os 5 agentes IA' },
          { icon: Crown, text: 'Exportação em DOCX' },
        ].map((item, i) => (
          <li key={i} className="flex items-center gap-3">
            <div className="w-6 h-6 bg-brand-100 dark:bg-brand-900/50 rounded-full flex items-center justify-center">
              <item.icon className="w-3 h-3 text-brand-600" />
            </div>
            <span className="text-sm text-gray-700 dark:text-gray-300">{item.text}</span>
          </li>
        ))}
      </ul>

      <button
        onClick={onUpgrade}
        className="w-full py-3 px-4 bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-xl transition-colors"
      >
        Começar por R$49/mês
      </button>

      <p className="text-center text-xs text-gray-500 dark:text-gray-400 mt-3">
        Cancele a qualquer momento • Sem taxas ocultas
      </p>
    </div>
  );
}
