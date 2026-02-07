'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Check, 
  Crown, 
  Zap, 
  Building2, 
  CreditCard,
  Calendar,
  AlertTriangle,
  ArrowRight,
  Loader2,
} from 'lucide-react';
import { toast } from 'sonner';
import { useBilling, type PlanTier, type BillingCycle } from '@/services/billing-service';

export default function BillingPage() {
  const router = useRouter();
  const { 
    plans, 
    subscription, 
    loading, 
    error, 
    upgrade, 
    cancel,
    currentTier,
    usage,
  } = useBilling();
  
  const [selectedCycle, setSelectedCycle] = useState<BillingCycle>('monthly');
  const [upgrading, setUpgrading] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);

  const handleUpgrade = async (tier: PlanTier) => {
    if (tier === 'free' || tier === currentTier) return;
    
    setUpgrading(tier);
    try {
      await upgrade(tier, selectedCycle);
    } catch (err) {
      toast.error('Erro ao iniciar checkout');
      setUpgrading(null);
    }
  };

  const handleCancel = async () => {
    if (!confirm('Tem certeza que deseja cancelar sua assinatura?')) return;
    
    setCancelling(true);
    try {
      const result = await cancel(false);
      toast.success(result.message);
    } catch (err) {
      toast.error('Erro ao cancelar assinatura');
    } finally {
      setCancelling(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  const getPlanIcon = (tier: PlanTier) => {
    switch (tier) {
      case 'free': return <Zap className="w-6 h-6" />;
      case 'pro': return <Crown className="w-6 h-6" />;
      case 'enterprise': return <Building2 className="w-6 h-6" />;
    }
  };

  const getPlanColor = (tier: PlanTier) => {
    switch (tier) {
      case 'free': return 'text-gray-500 bg-gray-100 dark:bg-gray-800';
      case 'pro': return 'text-brand-500 bg-brand-100 dark:bg-brand-900/30';
      case 'enterprise': return 'text-purple-500 bg-purple-100 dark:bg-purple-900/30';
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Planos e Faturamento
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Gerencie sua assinatura e veja seu uso atual
        </p>
      </div>

      {/* Current Plan Summary */}
      {subscription && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                Plano Atual
              </p>
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${getPlanColor(currentTier)}`}>
                  {getPlanIcon(currentTier)}
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white capitalize">
                    {currentTier}
                  </h2>
                  {subscription.cycle && (
                    <p className="text-sm text-gray-500">
                      Cobrança {subscription.cycle === 'monthly' ? 'mensal' : 'anual'}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Usage */}
            {usage && (
              <div className="flex-1 max-w-xs">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-gray-600 dark:text-gray-400">Uso este mês</span>
                  <span className={`font-medium ${
                    usage.is_at_limit ? 'text-red-500' : 'text-gray-900 dark:text-white'
                  }`}>
                    {usage.used} / {usage.limit === -1 ? '∞' : usage.limit}
                  </span>
                </div>
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all ${
                      usage.is_at_limit ? 'bg-red-500' : 
                      usage.should_show_upgrade ? 'bg-yellow-500' : 'bg-brand-500'
                    }`}
                    style={{ width: `${Math.min(usage.usage_percent, 100)}%` }}
                  />
                </div>
              </div>
            )}

            {/* Actions */}
            {currentTier !== 'free' && (
              <button
                onClick={handleCancel}
                disabled={cancelling}
                className="text-sm text-gray-500 hover:text-red-500 transition-colors disabled:opacity-50"
              >
                {cancelling ? 'Cancelando...' : 'Cancelar assinatura'}
              </button>
            )}
          </div>

          {/* Expiration warning */}
          {subscription.expires_at && (
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex items-center gap-2 text-sm">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span className="text-gray-600 dark:text-gray-400">
                Sua assinatura renova em {new Date(subscription.expires_at).toLocaleDateString('pt-BR')}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Billing Cycle Toggle */}
      <div className="flex justify-center mb-8">
        <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-1 inline-flex">
          <button
            onClick={() => setSelectedCycle('monthly')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              selectedCycle === 'monthly'
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow'
                : 'text-gray-600 dark:text-gray-400'
            }`}
          >
            Mensal
          </button>
          <button
            onClick={() => setSelectedCycle('yearly')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              selectedCycle === 'yearly'
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow'
                : 'text-gray-600 dark:text-gray-400'
            }`}
          >
            Anual
            <span className="ml-1 text-xs text-green-500 font-normal">-17%</span>
          </button>
        </div>
      </div>

      {/* Plans Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        {plans.map((plan) => {
          const isCurrentPlan = plan.tier === currentTier;
          const price = (plan as any).price ?? plan.price_monthly ?? 0;
          const yearlyPrice = plan.price_yearly ?? Math.round(price * 10);
          const displayPrice = selectedCycle === 'monthly' ? price : yearlyPrice;
          const isPro = plan.tier === 'pro';
          
          return (
            <div
              key={plan.tier || plan.id}
              className={`relative rounded-2xl border-2 p-6 transition-all ${
                isPro
                  ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-900/10 scale-105'
                  : 'border-gray-200 dark:border-gray-700'
              }`}
            >
              {isPro && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="px-3 py-1 bg-brand-500 text-white text-xs font-medium rounded-full">
                    Mais Popular
                  </span>
                </div>
              )}

              {/* Icon */}
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${getPlanColor(plan.tier)}`}>
                {getPlanIcon(plan.tier)}
              </div>

              {/* Info */}
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                {plan.name}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 mb-4">
                {plan.description}
              </p>

              {/* Price */}
              <div className="mb-6">
                {displayPrice > 0 ? (
                  <div className="flex items-baseline">
                    <span className="text-3xl font-bold text-gray-900 dark:text-white">
                      R${displayPrice}
                    </span>
                    <span className="text-gray-500 dark:text-gray-400 ml-1">
                      /{selectedCycle === 'monthly' ? 'mês' : 'ano'}
                    </span>
                  </div>
                ) : (
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">
                    Grátis
                  </span>
                )}
              </div>

              {/* Features */}
              <ul className="space-y-3 mb-6">
                {(Array.isArray(plan.features) ? plan.features : []).map((feature: string, idx: number) => (
                  <li key={idx} className="flex items-start gap-2">
                    <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <button
                onClick={() => handleUpgrade(plan.tier)}
                disabled={isCurrentPlan || plan.tier === 'free' || upgrading !== null}
                className={`w-full py-3 px-4 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${
                  isCurrentPlan
                    ? 'bg-gray-100 dark:bg-gray-800 text-gray-500 cursor-default'
                    : isPro
                    ? 'bg-brand-500 hover:bg-brand-600 text-white'
                    : 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white'
                } disabled:opacity-50`}
              >
                {upgrading === plan.tier ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Processando...
                  </>
                ) : isCurrentPlan ? (
                  'Plano Atual'
                ) : plan.tier === 'free' ? (
                  'Plano Gratuito'
                ) : plan.tier === 'enterprise' ? (
                  'Falar com Vendas'
                ) : (
                  <>
                    Fazer Upgrade
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          );
        })}
      </div>

      {/* Payment Methods */}
      <div className="mt-12 text-center">
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          Pagamento seguro via Mercado Pago
        </p>
        <div className="flex items-center justify-center gap-4 text-gray-400">
          <CreditCard className="w-8 h-8" />
          <span className="text-xs">Cartão de Crédito • PIX • Boleto</span>
        </div>
      </div>
    </div>
  );
}
