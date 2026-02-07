/**
 * Billing Service - Frontend integration with Mercado Pago
 */

import { apiClient } from './api-client';

// ==================== TYPES ====================

export type PlanTier = 'free' | 'pro' | 'enterprise';
export type BillingCycle = 'monthly' | 'yearly';
export type SubscriptionStatus = 'active' | 'pending' | 'paused' | 'cancelled' | 'expired';

export interface PlanFeatures {
  analyses_per_month: number;
  agents_available: number;
  export_formats: string[];
  priority_level: string;
  api_access: boolean;
  custom_agents: boolean;
  dedicated_support: boolean;
  sla_guarantee: boolean;
  refine_messages_per_analysis: number; // -1 = ilimitado
}

export interface Plan {
  id: string;
  tier: PlanTier;
  name: string;
  description: string;
  price_monthly: number;
  price_yearly: number;
  features: PlanFeatures;
}

export interface UsageInfo {
  within_limits: boolean;
  usage_percent: number;
  used: number;
  limit: number;
  remaining: number;
  should_show_upgrade: boolean;
  is_at_limit: boolean;
}

export interface SubscriptionStatusResponse {
  tier: PlanTier;
  status: SubscriptionStatus;
  cycle: BillingCycle | null;
  expires_at: string | null;
  usage: UsageInfo;
}

export interface CheckoutResponse {
  checkout_url: string;
  sandbox_url: string | null;
  preference_id: string;
  plan: {
    tier: PlanTier;
    name: string;
    price: number;
    cycle: BillingCycle;
  };
}

// ==================== SERVICE ====================

export const billingService = {
  /**
   * Lista todos os planos disponíveis
   */
  async getPlans(): Promise<{ plans: Plan[]; currency: string }> {
    const response = await apiClient.get<{ plans: Plan[]; currency: string }>('/billing/plans');
    return response.data;
  },

  /**
   * Retorna detalhes de um plano específico
   */
  async getPlanDetails(tier: PlanTier): Promise<Plan> {
    const response = await apiClient.get<Plan>(`/billing/plans/${tier}`);
    return response.data;
  },

  /**
   * Cria checkout para upgrade de plano
   * Retorna URL do Mercado Pago para redirecionamento
   */
  async createCheckout(
    planTier: PlanTier,
    cycle: BillingCycle = 'monthly'
  ): Promise<CheckoutResponse> {
    const response = await apiClient.post<CheckoutResponse>('/billing/checkout', {
      plan_tier: planTier,
      cycle,
    });
    return response.data;
  },

  /**
   * Retorna status atual da assinatura
   */
  async getSubscriptionStatus(): Promise<SubscriptionStatusResponse> {
    const response = await apiClient.get<SubscriptionStatusResponse>('/billing/status');
    return response.data;
  },

  /**
   * Retorna uso atual do plano
   */
  async getUsage(): Promise<UsageInfo> {
    const response = await apiClient.get<UsageInfo>('/billing/usage');
    return response.data;
  },

  /**
   * Cancela a assinatura
   * @param immediate - Se true, faz downgrade imediato
   */
  async cancelSubscription(immediate: boolean = false): Promise<{
    cancelled: boolean;
    message: string;
  }> {
    const response = await apiClient.post<{ cancelled: boolean; message: string }>('/billing/cancel', {
      immediate,
    });
    return response.data;
  },

  /**
   * Pausa a assinatura temporariamente
   */
  async pauseSubscription(): Promise<{ status: string }> {
    const response = await apiClient.post<{ status: string }>('/billing/pause');
    return response.data;
  },

  /**
   * Retoma uma assinatura pausada
   */
  async resumeSubscription(): Promise<{ status: string }> {
    const response = await apiClient.post<{ status: string }>('/billing/resume');
    return response.data;
  },

  /**
   * Inicia o fluxo de checkout
   * Redireciona para o Mercado Pago
   */
  async startCheckout(planTier: PlanTier, cycle: BillingCycle = 'monthly'): Promise<void> {
    const checkout = await this.createCheckout(planTier, cycle);
    
    // Usa sandbox em desenvolvimento
    const checkoutUrl = process.env.NODE_ENV === 'development' 
      ? checkout.sandbox_url || checkout.checkout_url
      : checkout.checkout_url;
    
    // Redireciona para o Mercado Pago
    window.location.href = checkoutUrl;
  },
};

// ==================== HOOKS ====================

import { useState, useEffect, useCallback } from 'react';

/**
 * Hook para gerenciar estado de billing
 */
export function useBilling() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [subscription, setSubscription] = useState<SubscriptionStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [plansData, statusData] = await Promise.all([
        billingService.getPlans(),
        billingService.getSubscriptionStatus(),
      ]);
      
      setPlans(plansData.plans);
      setSubscription(statusData);
    } catch (err) {
      setError('Erro ao carregar dados de billing');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const upgrade = async (tier: PlanTier, cycle: BillingCycle = 'monthly') => {
    await billingService.startCheckout(tier, cycle);
  };

  const cancel = async (immediate: boolean = false) => {
    const result = await billingService.cancelSubscription(immediate);
    await fetchData(); // Refresh data
    return result;
  };

  return {
    plans,
    subscription,
    loading,
    error,
    upgrade,
    cancel,
    refresh: fetchData,
    currentTier: subscription?.tier || 'free',
    usage: subscription?.usage || null,
    isAtLimit: subscription?.usage?.is_at_limit || false,
    shouldShowUpgrade: subscription?.usage?.should_show_upgrade || false,
  };
}

/**
 * Hook para verificar se pode fazer uma ação baseado no plano
 */
export function useCanPerformAction() {
  const { subscription } = useBilling();
  
  const canCreateAnalysis = useCallback(() => {
    if (!subscription) return true; // Otimista enquanto carrega
    return subscription.usage.within_limits;
  }, [subscription]);

  const canExportFormat = useCallback((format: string) => {
    if (!subscription) return false;
    const plan = subscription.tier;
    
    const formatsByPlan: Record<PlanTier, string[]> = {
      free: ['PDF'],
      pro: ['PDF', 'DOCX', 'Excel'],
      enterprise: ['PDF', 'DOCX', 'Excel', 'API'],
    };
    
    return formatsByPlan[plan]?.includes(format) || false;
  }, [subscription]);

  const hasApiAccess = useCallback(() => {
    if (!subscription) return false;
    return subscription.tier !== 'free';
  }, [subscription]);

  return {
    canCreateAnalysis,
    canExportFormat,
    hasApiAccess,
  };
}

export default billingService;
