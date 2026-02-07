'use client';

import { useState } from 'react';
import { X, Check, Zap, Crown, Sparkles, Building2 } from 'lucide-react';

interface Plan {
  id: string;
  name: string;
  price: number;
  period: string;
  description: string;
  features: string[];
  highlighted?: boolean;
  cta: string;
}

const PLANS: Plan[] = [
  {
    id: 'starter',
    name: 'Starter',
    price: 49,
    period: '/mês',
    description: 'Para empreendedores e pequenas equipes',
    features: [
      '20 análises por mês',
      'Todos os 5 agentes IA',
      'Exportação PDF e DOCX',
      'Prioridade média',
      'Suporte por email',
    ],
    cta: 'Começar Starter',
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 149,
    period: '/mês',
    description: 'Para equipes em crescimento',
    features: [
      '100 análises por mês',
      'Todos os 5 agentes IA',
      'Exportação completa + Excel',
      'Prioridade alta',
      'Suporte prioritário',
      'API Access',
    ],
    highlighted: true,
    cta: 'Começar Professional',
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 0,
    period: 'Personalizado',
    description: 'Para grandes organizações',
    features: [
      'Análises ilimitadas',
      'Agentes personalizados',
      'Integrações customizadas',
      'SLA garantido',
      'Gerente de conta dedicado',
      'Treinamento incluso',
    ],
    cta: 'Falar com Vendas',
  },
];

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectPlan?: (planId: string) => void;
  highlightedFeature?: string;
}

export function UpgradeModal({ 
  isOpen, 
  onClose, 
  onSelectPlan,
  highlightedFeature 
}: UpgradeModalProps) {
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleSelectPlan = async (planId: string) => {
    setSelectedPlan(planId);
    setIsLoading(true);
    
    // Simula chamada de API
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    if (onSelectPlan) {
      onSelectPlan(planId);
    }
    
    // Aqui iria redirecionar para Stripe ou checkout
    window.location.href = `/checkout?plan=${planId}`;
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-5xl my-8">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Escolha seu plano
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Desbloqueie todo o potencial da análise com IA
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Plans Grid */}
        <div className="p-6">
          <div className="grid md:grid-cols-3 gap-6">
            {PLANS.map((plan) => (
              <div
                key={plan.id}
                className={`relative rounded-2xl border-2 p-6 transition-all ${
                  plan.highlighted
                    ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-900/20 scale-105'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                }`}
              >
                {plan.highlighted && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="px-3 py-1 bg-brand-500 text-white text-xs font-medium rounded-full">
                      Mais Popular
                    </span>
                  </div>
                )}

                {/* Plan Icon */}
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${
                  plan.id === 'starter' ? 'bg-blue-100 dark:bg-blue-900/30' :
                  plan.id === 'professional' ? 'bg-brand-100 dark:bg-brand-900/30' :
                  'bg-purple-100 dark:bg-purple-900/30'
                }`}>
                  {plan.id === 'starter' && <Zap className="w-6 h-6 text-blue-500" />}
                  {plan.id === 'professional' && <Sparkles className="w-6 h-6 text-brand-500" />}
                  {plan.id === 'enterprise' && <Building2 className="w-6 h-6 text-purple-500" />}
                </div>

                {/* Plan Info */}
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                  {plan.name}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 mb-4">
                  {plan.description}
                </p>

                {/* Price */}
                <div className="mb-6">
                  {plan.price > 0 ? (
                    <div className="flex items-baseline">
                      <span className="text-3xl font-bold text-gray-900 dark:text-white">
                        R${plan.price}
                      </span>
                      <span className="text-gray-500 dark:text-gray-400 ml-1">
                        {plan.period}
                      </span>
                    </div>
                  ) : (
                    <span className="text-xl font-semibold text-gray-900 dark:text-white">
                      {plan.period}
                    </span>
                  )}
                </div>

                {/* Features */}
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <Check className={`w-5 h-5 flex-shrink-0 ${
                        plan.highlighted ? 'text-brand-500' : 'text-green-500'
                      }`} />
                      <span className={`text-sm ${
                        highlightedFeature && feature.includes(highlightedFeature)
                          ? 'font-medium text-brand-600 dark:text-brand-400'
                          : 'text-gray-600 dark:text-gray-400'
                      }`}>
                        {feature}
                      </span>
                    </li>
                  ))}
                </ul>

                {/* CTA */}
                <button
                  onClick={() => handleSelectPlan(plan.id)}
                  disabled={isLoading && selectedPlan === plan.id}
                  className={`w-full py-3 px-4 rounded-xl font-medium transition-all ${
                    plan.highlighted
                      ? 'bg-brand-500 hover:bg-brand-600 text-white'
                      : 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white'
                  } disabled:opacity-50`}
                >
                  {isLoading && selectedPlan === plan.id ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                      Processando...
                    </span>
                  ) : (
                    plan.cta
                  )}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 rounded-b-2xl">
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-green-500" />
              Cancele a qualquer momento
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-green-500" />
              Garantia de 7 dias
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-green-500" />
              Suporte em português
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Componente simplificado para CTA inline
export function UpgradeBanner({ 
  message = "Desbloqueie análises ilimitadas",
  onUpgrade 
}: { 
  message?: string;
  onUpgrade?: () => void;
}) {
  return (
    <div className="bg-gradient-to-r from-brand-500 to-purple-500 rounded-xl p-4 text-white">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Crown className="w-6 h-6" />
          <span className="font-medium">{message}</span>
        </div>
        <button
          onClick={onUpgrade}
          className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg font-medium transition-colors"
        >
          Fazer Upgrade
        </button>
      </div>
    </div>
  );
}
