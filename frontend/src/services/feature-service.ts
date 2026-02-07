/**
 * Feature Service - Frontend feature flags management
 * Integra com billing para controle de acesso por plano
 */

import { apiClient } from './api-client';

// ==================== TYPES ====================

export type PlanTier = 'free' | 'pro' | 'enterprise';

export enum Feature {
  // Análises
  CREATE_ANALYSIS = 'create_analysis',
  EXPORT_PDF = 'export_pdf',
  EXPORT_DOCX = 'export_docx',
  EXPORT_EXCEL = 'export_excel',
  EXPORT_API = 'export_api',

  // Agentes IA
  AGENT_MARKET = 'agent_market',
  AGENT_FINANCIAL = 'agent_financial',
  AGENT_MARKETING = 'agent_marketing',
  AGENT_RISK = 'agent_risk',
  AGENT_PLANNING = 'agent_planning',
  CUSTOM_AGENTS = 'custom_agents',

  // API & Integrações
  API_ACCESS = 'api_access',
  WEBHOOKS = 'webhooks',
  INTEGRATIONS = 'integrations',

  // Relatórios
  ADVANCED_REPORTS = 'advanced_reports',
  SCHEDULED_REPORTS = 'scheduled_reports',
  WHITE_LABEL = 'white_label',

  // Suporte
  PRIORITY_SUPPORT = 'priority_support',
  DEDICATED_SUPPORT = 'dedicated_support',
  SLA_GUARANTEE = 'sla_guarantee',

  // Colaboração
  TEAM_MEMBERS = 'team_members',
  SHARED_ANALYSES = 'shared_analyses',
  COMMENTS = 'comments',

  // Histórico
  ANALYSIS_HISTORY = 'analysis_history',
  UNLIMITED_HISTORY = 'unlimited_history',
}

export interface FeatureInfo {
  feature: string;
  name: string;
  description: string;
  enabled: boolean;
  limit: number | null;
  is_unlimited: boolean;
  min_plan: PlanTier;
  current_usage?: number;
  remaining?: number;
  usage_percent?: number;
  is_at_limit?: boolean;
  upgrade_message?: string;
}

export interface FeatureError {
  error: true;
  error_code: string;
  message: string;
  feature: string | null;
  current_plan: PlanTier | null;
  required_plan: PlanTier | null;
  upgrade_required: boolean;
  limit?: number;
  current_usage?: number;
}

export interface PlanComparison {
  current_plan: PlanTier;
  target_plan: PlanTier;
  new_features: Array<{
    feature: string;
    name: string;
    description: string;
  }>;
  improved_limits: Array<{
    feature: string;
    name: string;
    current_limit: number;
    new_limit: number | string;
  }>;
  total_new_features: number;
  total_improved_limits: number;
}

// ==================== FEATURE FLAGS CONFIGURATION (CLIENT-SIDE) ====================

interface FeatureFlagConfig {
  name: string;
  description: string;
  availableIn: PlanTier[];
  limits?: Partial<Record<PlanTier, number | null>>;
  upgradeMessage: string;
  minPlan: PlanTier;
}

const FEATURE_FLAGS: Record<Feature, FeatureFlagConfig> = {
  [Feature.CREATE_ANALYSIS]: {
    name: 'Criar Análises',
    description: 'Criar novas análises de negócio',
    availableIn: ['free', 'pro', 'enterprise'],
    limits: { free: 3, pro: 50, enterprise: null },
    upgradeMessage: 'Você atingiu o limite de análises.',
    minPlan: 'pro',
  },
  [Feature.EXPORT_PDF]: {
    name: 'Exportar PDF',
    description: 'Exportar análises em PDF',
    availableIn: ['free', 'pro', 'enterprise'],
    upgradeMessage: '',
    minPlan: 'free',
  },
  [Feature.EXPORT_DOCX]: {
    name: 'Exportar Word',
    description: 'Exportar análises em DOCX',
    availableIn: ['pro', 'enterprise'],
    upgradeMessage: 'Exportação em Word disponível a partir do plano Pro.',
    minPlan: 'pro',
  },
  [Feature.EXPORT_EXCEL]: {
    name: 'Exportar Excel',
    description: 'Exportar dados em Excel',
    availableIn: ['pro', 'enterprise'],
    upgradeMessage: 'Exportação em Excel disponível a partir do plano Pro.',
    minPlan: 'pro',
  },
  [Feature.EXPORT_API]: {
    name: 'Exportar via API',
    description: 'Exportar dados via API',
    availableIn: ['enterprise'],
    upgradeMessage: 'Exportação via API disponível no plano Enterprise.',
    minPlan: 'enterprise',
  },
  [Feature.AGENT_MARKET]: {
    name: 'Agente de Mercado',
    description: 'Análise de mercado e competidores',
    availableIn: ['free', 'pro', 'enterprise'],
    upgradeMessage: '',
    minPlan: 'free',
  },
  [Feature.AGENT_FINANCIAL]: {
    name: 'Agente Financeiro',
    description: 'Análise financeira',
    availableIn: ['free', 'pro', 'enterprise'],
    upgradeMessage: '',
    minPlan: 'free',
  },
  [Feature.AGENT_MARKETING]: {
    name: 'Agente de Marketing',
    description: 'Estratégias de marketing',
    availableIn: ['free', 'pro', 'enterprise'],
    upgradeMessage: '',
    minPlan: 'free',
  },
  [Feature.AGENT_RISK]: {
    name: 'Agente de Riscos',
    description: 'Análise e mitigação de riscos',
    availableIn: ['pro', 'enterprise'],
    upgradeMessage: 'Agente de Riscos disponível a partir do plano Pro.',
    minPlan: 'pro',
  },
  [Feature.AGENT_PLANNING]: {
    name: 'Agente de Planejamento',
    description: 'Planejamento estratégico',
    availableIn: ['pro', 'enterprise'],
    upgradeMessage: 'Agente de Planejamento disponível a partir do plano Pro.',
    minPlan: 'pro',
  },
  [Feature.CUSTOM_AGENTS]: {
    name: 'Agentes Customizados',
    description: 'Criar agentes personalizados',
    availableIn: ['enterprise'],
    upgradeMessage: 'Agentes customizados disponíveis no plano Enterprise.',
    minPlan: 'enterprise',
  },
  [Feature.API_ACCESS]: {
    name: 'Acesso à API',
    description: 'Acesso programático via API',
    availableIn: ['pro', 'enterprise'],
    limits: { pro: 1000, enterprise: null },
    upgradeMessage: 'Acesso à API disponível a partir do plano Pro.',
    minPlan: 'pro',
  },
  [Feature.WEBHOOKS]: {
    name: 'Webhooks',
    description: 'Notificações em tempo real',
    availableIn: ['pro', 'enterprise'],
    limits: { pro: 5, enterprise: null },
    upgradeMessage: 'Webhooks disponíveis a partir do plano Pro.',
    minPlan: 'pro',
  },
  [Feature.INTEGRATIONS]: {
    name: 'Integrações',
    description: 'Integrar com ferramentas externas',
    availableIn: ['enterprise'],
    upgradeMessage: 'Integrações disponíveis no plano Enterprise.',
    minPlan: 'enterprise',
  },
  [Feature.ADVANCED_REPORTS]: {
    name: 'Relatórios Avançados',
    description: 'Relatórios detalhados',
    availableIn: ['pro', 'enterprise'],
    upgradeMessage: 'Relatórios avançados disponíveis a partir do plano Pro.',
    minPlan: 'pro',
  },
  [Feature.SCHEDULED_REPORTS]: {
    name: 'Relatórios Agendados',
    description: 'Envio automático de relatórios',
    availableIn: ['enterprise'],
    upgradeMessage: 'Relatórios agendados disponíveis no plano Enterprise.',
    minPlan: 'enterprise',
  },
  [Feature.WHITE_LABEL]: {
    name: 'White Label',
    description: 'Relatórios com sua marca',
    availableIn: ['enterprise'],
    upgradeMessage: 'White label disponível no plano Enterprise.',
    minPlan: 'enterprise',
  },
  [Feature.PRIORITY_SUPPORT]: {
    name: 'Suporte Prioritário',
    description: 'Atendimento prioritário',
    availableIn: ['pro', 'enterprise'],
    upgradeMessage: 'Suporte prioritário disponível a partir do plano Pro.',
    minPlan: 'pro',
  },
  [Feature.DEDICATED_SUPPORT]: {
    name: 'Suporte Dedicado',
    description: 'Gerente de conta dedicado',
    availableIn: ['enterprise'],
    upgradeMessage: 'Suporte dedicado disponível no plano Enterprise.',
    minPlan: 'enterprise',
  },
  [Feature.SLA_GUARANTEE]: {
    name: 'SLA Garantido',
    description: 'Garantia de tempo de resposta',
    availableIn: ['enterprise'],
    upgradeMessage: 'SLA garantido disponível no plano Enterprise.',
    minPlan: 'enterprise',
  },
  [Feature.TEAM_MEMBERS]: {
    name: 'Membros da Equipe',
    description: 'Adicionar membros',
    availableIn: ['free', 'pro', 'enterprise'],
    limits: { free: 1, pro: 5, enterprise: null },
    upgradeMessage: 'Adicione mais membros fazendo upgrade.',
    minPlan: 'pro',
  },
  [Feature.SHARED_ANALYSES]: {
    name: 'Análises Compartilhadas',
    description: 'Compartilhar análises',
    availableIn: ['pro', 'enterprise'],
    upgradeMessage: 'Compartilhamento disponível a partir do plano Pro.',
    minPlan: 'pro',
  },
  [Feature.COMMENTS]: {
    name: 'Comentários',
    description: 'Adicionar comentários',
    availableIn: ['pro', 'enterprise'],
    upgradeMessage: 'Comentários disponíveis a partir do plano Pro.',
    minPlan: 'pro',
  },
  [Feature.ANALYSIS_HISTORY]: {
    name: 'Histórico de Análises',
    description: 'Acessar análises anteriores',
    availableIn: ['free', 'pro', 'enterprise'],
    limits: { free: 10, pro: 100, enterprise: null },
    upgradeMessage: 'Acesse mais histórico fazendo upgrade.',
    minPlan: 'pro',
  },
  [Feature.UNLIMITED_HISTORY]: {
    name: 'Histórico Ilimitado',
    description: 'Todo histórico de análises',
    availableIn: ['enterprise'],
    upgradeMessage: 'Histórico ilimitado disponível no plano Enterprise.',
    minPlan: 'enterprise',
  },
};

// ==================== SERVICE ====================

export const featureService = {
  /**
   * Verifica se uma feature está disponível (client-side, sem API call)
   */
  isEnabled(feature: Feature, plan: PlanTier): boolean {
    const config = FEATURE_FLAGS[feature];
    return config?.availableIn.includes(plan) ?? false;
  },

  /**
   * Retorna o limite de uma feature para o plano
   */
  getLimit(feature: Feature, plan: PlanTier): number | null {
    const config = FEATURE_FLAGS[feature];
    return config?.limits?.[plan] ?? null;
  },

  /**
   * Retorna configuração de uma feature
   */
  getFeatureConfig(feature: Feature): FeatureFlagConfig | null {
    return FEATURE_FLAGS[feature] ?? null;
  },

  /**
   * Lista features disponíveis para um plano
   */
  getAvailableFeatures(plan: PlanTier): Feature[] {
    return Object.entries(FEATURE_FLAGS)
      .filter(([_, config]) => config.availableIn.includes(plan))
      .map(([feature]) => feature as Feature);
  },

  /**
   * Lista features bloqueadas para um plano
   */
  getLockedFeatures(plan: PlanTier): Feature[] {
    return Object.entries(FEATURE_FLAGS)
      .filter(([_, config]) => !config.availableIn.includes(plan))
      .map(([feature]) => feature as Feature);
  },

  // ==================== API CALLS ====================

  /**
   * Busca todas as features do servidor
   */
  async fetchAllFeatures(): Promise<Record<string, FeatureInfo>> {
    const response = await apiClient.get<{ features: Record<string, FeatureInfo> }>('/features/');
    return response.data.features;
  },

  /**
   * Verifica uma feature específica no servidor
   */
  async checkFeature(feature: Feature): Promise<FeatureInfo> {
    const response = await apiClient.get<FeatureInfo>(`/features/check/${feature}`);
    return response.data;
  },

  /**
   * Busca uso atual de features
   */
  async fetchUsage(): Promise<Record<string, unknown>> {
    const response = await apiClient.get<Record<string, unknown>>('/features/usage');
    return response.data;
  },

  /**
   * Compara planos
   */
  async comparePlans(targetPlan: PlanTier): Promise<PlanComparison> {
    const response = await apiClient.get<PlanComparison>('/features/compare', {
      params: { target_plan: targetPlan },
    });
    return response.data;
  },
};

// ==================== REACT HOOKS ====================

import { useState, useEffect, useCallback, useMemo } from 'react';

/**
 * Hook para verificar se uma feature está disponível
 */
export function useFeature(feature: Feature, plan: PlanTier) {
  const isEnabled = useMemo(() => featureService.isEnabled(feature, plan), [feature, plan]);
  const config = useMemo(() => featureService.getFeatureConfig(feature), [feature]);
  const limit = useMemo(() => featureService.getLimit(feature, plan), [feature, plan]);

  return {
    isEnabled,
    limit,
    isUnlimited: limit === null && isEnabled,
    config,
    upgradeMessage: config?.upgradeMessage,
    minPlan: config?.minPlan,
  };
}

/**
 * Hook para gerenciar features com dados do servidor
 */
export function useFeatures(plan: PlanTier) {
  const [features, setFeatures] = useState<Record<string, FeatureInfo>>({});
  const [usage, setUsage] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [featuresData, usageData] = await Promise.all([
        featureService.fetchAllFeatures(),
        featureService.fetchUsage(),
      ]);
      setFeatures(featuresData);
      setUsage(usageData.usage || {});
      setError(null);
    } catch (err) {
      setError('Erro ao carregar features');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const isEnabled = useCallback(
    (feature: Feature) => featureService.isEnabled(feature, plan),
    [plan]
  );

  const checkLimit = useCallback(
    (feature: Feature, currentUsage: number) => {
      const limit = featureService.getLimit(feature, plan);
      if (limit === null) return true;
      return currentUsage < limit;
    },
    [plan]
  );

  const getRemaining = useCallback(
    (feature: Feature) => {
      const limit = featureService.getLimit(feature, plan);
      if (limit === null) return null;
      const used = usage[feature]?.current || 0;
      return Math.max(0, limit - used);
    },
    [plan, usage]
  );

  return {
    features,
    usage,
    loading,
    error,
    isEnabled,
    checkLimit,
    getRemaining,
    refresh: fetchData,
    availableFeatures: featureService.getAvailableFeatures(plan),
    lockedFeatures: featureService.getLockedFeatures(plan),
  };
}

/**
 * Hook para comparação de planos
 */
export function usePlanComparison(currentPlan: PlanTier, targetPlan: PlanTier) {
  const [comparison, setComparison] = useState<PlanComparison | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (currentPlan === targetPlan) {
      setComparison(null);
      return;
    }

    setLoading(true);
    featureService
      .comparePlans(targetPlan)
      .then(setComparison)
      .catch(() => setComparison(null))
      .finally(() => setLoading(false));
  }, [currentPlan, targetPlan]);

  return { comparison, loading };
}

export default featureService;
