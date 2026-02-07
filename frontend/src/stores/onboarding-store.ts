/**
 * Onboarding Store - Estado e progresso do onboarding
 * 
 * Foco em:
 * - Reduzir churn: Guiar usuário até primeiro valor
 * - Aumentar ativação: Completar primeira análise
 * - Mostrar valor rápido: Wizard focado e objetivo
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
}

interface OnboardingState {
  // Estado do wizard
  isOnboardingComplete: boolean;
  currentStep: number;
  showWizard: boolean;
  
  // Steps do onboarding
  steps: OnboardingStep[];
  
  // Métricas de conversão
  firstAnalysisCompleted: boolean;
  upgradePromptsSeen: number;
  daysOnFreePlan: number;
  
  // Actions
  setCurrentStep: (step: number) => void;
  completeStep: (stepId: string) => void;
  completeOnboarding: () => void;
  skipOnboarding: () => void;
  showUpgradePrompt: () => void;
  resetOnboarding: () => void;
  setFirstAnalysisCompleted: () => void;
}

const DEFAULT_STEPS: OnboardingStep[] = [
  {
    id: 'welcome',
    title: 'Bem-vindo!',
    description: 'Conheça o Consultor Multi-Agentes',
    completed: false,
  },
  {
    id: 'profile',
    title: 'Seu perfil',
    description: 'Conte-nos sobre seu negócio',
    completed: false,
  },
  {
    id: 'first-analysis',
    title: 'Primeira análise',
    description: 'Experimente o poder da IA',
    completed: false,
  },
  {
    id: 'explore',
    title: 'Explore',
    description: 'Descubra mais recursos',
    completed: false,
  },
];

export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set, get) => ({
      isOnboardingComplete: false,
      currentStep: 0,
      showWizard: true,
      steps: DEFAULT_STEPS,
      firstAnalysisCompleted: false,
      upgradePromptsSeen: 0,
      daysOnFreePlan: 0,

      setCurrentStep: (step: number) => {
        set({ currentStep: step });
      },

      completeStep: (stepId: string) => {
        set((state) => ({
          steps: state.steps.map((s) =>
            s.id === stepId ? { ...s, completed: true } : s
          ),
          currentStep: Math.min(state.currentStep + 1, state.steps.length - 1),
        }));
      },

      completeOnboarding: () => {
        set({
          isOnboardingComplete: true,
          showWizard: false,
          steps: get().steps.map((s) => ({ ...s, completed: true })),
        });
      },

      skipOnboarding: () => {
        set({
          isOnboardingComplete: true,
          showWizard: false,
        });
      },

      showUpgradePrompt: () => {
        set((state) => ({
          upgradePromptsSeen: state.upgradePromptsSeen + 1,
        }));
      },

      resetOnboarding: () => {
        set({
          isOnboardingComplete: false,
          currentStep: 0,
          showWizard: true,
          steps: DEFAULT_STEPS,
          firstAnalysisCompleted: false,
        });
      },

      setFirstAnalysisCompleted: () => {
        set({ firstAnalysisCompleted: true });
        get().completeStep('first-analysis');
      },
    }),
    {
      name: 'onboarding-storage',
    }
  )
);

// Hook para verificar se deve mostrar onboarding
export function useShouldShowOnboarding(): boolean {
  const { isOnboardingComplete, showWizard } = useOnboardingStore();
  return !isOnboardingComplete && showWizard;
}

// Hook para calcular progresso
export function useOnboardingProgress(): number {
  const { steps } = useOnboardingStore();
  const completed = steps.filter((s) => s.completed).length;
  return Math.round((completed / steps.length) * 100);
}
