'use client';

import { ReactNode } from 'react';
import { Lock, Zap, Crown } from 'lucide-react';
import { Feature, featureService, type PlanTier } from '@/services/feature-service';

interface FeatureGateProps {
  feature: Feature;
  plan: PlanTier;
  children: ReactNode;
  fallback?: ReactNode;
  showLock?: boolean;
  onUpgradeClick?: () => void;
}

/**
 * Componente que bloqueia conteúdo baseado em feature flags.
 * 
 * Se a feature não está disponível:
 * - Mostra fallback se fornecido
 * - Ou mostra overlay de bloqueio com CTA de upgrade
 */
export function FeatureGate({
  feature,
  plan,
  children,
  fallback,
  showLock = true,
  onUpgradeClick,
}: FeatureGateProps) {
  const isEnabled = featureService.isEnabled(feature, plan);
  const config = featureService.getFeatureConfig(feature);

  if (isEnabled) {
    return <>{children}</>;
  }

  if (fallback) {
    return <>{fallback}</>;
  }

  if (!showLock) {
    return null;
  }

  return (
    <div className="relative">
      {/* Conteúdo bloqueado (blur) */}
      <div className="blur-sm pointer-events-none select-none opacity-50">
        {children}
      </div>

      {/* Overlay de bloqueio */}
      <div className="absolute inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-lg">
        <div className="text-center p-6 max-w-sm">
          <div className="w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="w-6 h-6 text-gray-400" />
          </div>
          
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
            {config?.name || 'Feature Bloqueada'}
          </h3>
          
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            {config?.upgradeMessage || 'Esta feature requer upgrade do plano.'}
          </p>

          <button
            onClick={onUpgradeClick}
            className="inline-flex items-center gap-2 px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-lg transition-colors"
          >
            <Zap className="w-4 h-4" />
            Fazer Upgrade
          </button>

          <p className="text-xs text-gray-400 mt-3">
            Disponível a partir do plano {config?.minPlan?.toUpperCase()}
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Componente que mostra badge de "Pro" ou "Enterprise" em features bloqueadas
 */
export function FeatureBadge({ 
  feature, 
  plan,
  className = '',
}: { 
  feature: Feature; 
  plan: PlanTier;
  className?: string;
}) {
  const isEnabled = featureService.isEnabled(feature, plan);
  const config = featureService.getFeatureConfig(feature);

  if (isEnabled) return null;

  const minPlan = config?.minPlan;
  
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full ${
      minPlan === 'enterprise' 
        ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400'
        : 'bg-brand-100 text-brand-700 dark:bg-brand-900/30 dark:text-brand-400'
    } ${className}`}>
      <Crown className="w-3 h-3" />
      {minPlan?.toUpperCase()}
    </span>
  );
}

/**
 * Wrapper para botões que requerem features específicas
 */
export function FeatureButton({
  feature,
  plan,
  children,
  onClick,
  onUpgradeClick,
  disabled = false,
  className = '',
  ...props
}: {
  feature: Feature;
  plan: PlanTier;
  children: ReactNode;
  onClick?: () => void;
  onUpgradeClick?: () => void;
  disabled?: boolean;
  className?: string;
  [key: string]: any;
}) {
  const isEnabled = featureService.isEnabled(feature, plan);
  const config = featureService.getFeatureConfig(feature);

  const handleClick = () => {
    if (isEnabled) {
      onClick?.();
    } else {
      onUpgradeClick?.();
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled}
      className={`relative ${className} ${!isEnabled ? 'opacity-75' : ''}`}
      title={!isEnabled ? config?.upgradeMessage : undefined}
      {...props}
    >
      {children}
      {!isEnabled && (
        <Lock className="w-3 h-3 absolute top-1 right-1 text-gray-400" />
      )}
    </button>
  );
}

/**
 * Lista de features com indicação de disponibilidade
 */
export function FeatureList({
  plan,
  features,
  showAll = false,
}: {
  plan: PlanTier;
  features?: Feature[];
  showAll?: boolean;
}) {
  const featuresToShow = features || (showAll 
    ? Object.values(Feature) 
    : featureService.getAvailableFeatures(plan));

  return (
    <ul className="space-y-2">
      {featuresToShow.map((feature) => {
        const isEnabled = featureService.isEnabled(feature, plan);
        const config = featureService.getFeatureConfig(feature);
        
        return (
          <li 
            key={feature}
            className={`flex items-center gap-3 ${
              isEnabled ? 'text-gray-900 dark:text-white' : 'text-gray-400'
            }`}
          >
            {isEnabled ? (
              <span className="w-5 h-5 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                <svg className="w-3 h-3 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </span>
            ) : (
              <span className="w-5 h-5 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
                <Lock className="w-3 h-3 text-gray-400" />
              </span>
            )}
            
            <span className="flex-1">{config?.name}</span>
            
            {!isEnabled && <FeatureBadge feature={feature} plan={plan} />}
          </li>
        );
      })}
    </ul>
  );
}

export default FeatureGate;
