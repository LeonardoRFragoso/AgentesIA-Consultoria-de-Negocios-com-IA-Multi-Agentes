'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useOnboardingStore, useOnboardingProgress } from '@/stores/onboarding-store';
import { useAuthStore } from '@/stores/auth-store';
import { 
  Sparkles, 
  Building2, 
  Rocket, 
  ArrowRight, 
  ArrowLeft,
  Check,
  X,
  Zap
} from 'lucide-react';

interface WizardStepProps {
  isActive: boolean;
  children: React.ReactNode;
}

function WizardStep({ isActive, children }: WizardStepProps) {
  if (!isActive) return null;
  return <div className="animate-fade-in">{children}</div>;
}

export function OnboardingWizard() {
  const router = useRouter();
  const { user } = useAuthStore();
  const { 
    currentStep, 
    setCurrentStep, 
    completeStep, 
    completeOnboarding,
    skipOnboarding,
    steps 
  } = useOnboardingStore();
  const progress = useOnboardingProgress();
  
  const [businessType, setBusinessType] = useState('B2B');
  const [teamSize, setTeamSize] = useState('1-10');

  const handleNext = () => {
    completeStep(steps[currentStep].id);
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      completeOnboarding();
      router.push('/dashboard');
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    skipOnboarding();
    router.push('/dashboard');
  };

  const handleStartFirstAnalysis = () => {
    completeOnboarding();
    router.push('/nova-analise?guided=true');
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden">
        {/* Progress bar */}
        <div className="h-1 bg-gray-200 dark:bg-gray-700">
          <div 
            className="h-full bg-brand-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                  index < currentStep
                    ? 'bg-brand-500 text-white'
                    : index === currentStep
                    ? 'bg-brand-100 text-brand-600 ring-2 ring-brand-500'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-400'
                }`}
              >
                {index < currentStep ? (
                  <Check className="w-4 h-4" />
                ) : (
                  index + 1
                )}
              </div>
            ))}
          </div>
          <button
            onClick={handleSkip}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 p-2"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-8 min-h-[400px]">
          {/* Step 1: Welcome */}
          <WizardStep isActive={currentStep === 0}>
            <div className="text-center">
              <div className="w-20 h-20 bg-brand-100 dark:bg-brand-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Sparkles className="w-10 h-10 text-brand-500" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                Olá, {user?.name || 'boas-vindas'}! 👋
              </h2>
              <p className="text-gray-600 dark:text-gray-400 text-lg mb-6 max-w-md mx-auto">
                Você está a poucos passos de transformar suas decisões de negócio 
                com insights de <strong>5 especialistas de IA</strong>.
              </p>
              
              <div className="grid grid-cols-3 gap-4 max-w-md mx-auto mb-8">
                {[
                  { icon: '📊', label: 'Análise Financeira' },
                  { icon: '🎯', label: 'Estratégia Comercial' },
                  { icon: '📈', label: 'Inteligência de Mercado' },
                ].map((item) => (
                  <div 
                    key={item.label}
                    className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center"
                  >
                    <span className="text-2xl mb-1 block">{item.icon}</span>
                    <span className="text-xs text-gray-600 dark:text-gray-400">{item.label}</span>
                  </div>
                ))}
              </div>

              <p className="text-sm text-gray-500 dark:text-gray-400">
                ⏱️ Leva menos de 2 minutos para configurar
              </p>
            </div>
          </WizardStep>

          {/* Step 2: Profile */}
          <WizardStep isActive={currentStep === 1}>
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Building2 className="w-8 h-8 text-purple-500" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Conte-nos sobre seu negócio
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Isso nos ajuda a personalizar suas análises
              </p>
            </div>

            <div className="space-y-6 max-w-md mx-auto">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Tipo de negócio
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {['B2B', 'B2C', 'SaaS', 'E-commerce'].map((type) => (
                    <button
                      key={type}
                      onClick={() => setBusinessType(type)}
                      className={`p-4 rounded-xl border-2 text-left transition-all ${
                        businessType === type
                          ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
                      }`}
                    >
                      <span className="font-medium text-gray-900 dark:text-white">{type}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Tamanho da equipe
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {['1-10', '11-50', '50+'].map((size) => (
                    <button
                      key={size}
                      onClick={() => setTeamSize(size)}
                      className={`p-3 rounded-xl border-2 transition-all ${
                        teamSize === size
                          ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
                      }`}
                    >
                      <span className="font-medium text-gray-900 dark:text-white">{size}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </WizardStep>

          {/* Step 3: First Analysis */}
          <WizardStep isActive={currentStep === 2}>
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Rocket className="w-8 h-8 text-green-500" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Pronto para sua primeira análise?
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Vamos criar uma análise juntos em menos de 5 minutos
              </p>
            </div>

            <div className="bg-gradient-to-r from-brand-50 to-purple-50 dark:from-brand-900/20 dark:to-purple-900/20 rounded-2xl p-6 max-w-md mx-auto mb-8">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-white dark:bg-gray-800 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Zap className="w-5 h-5 text-yellow-500" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                    Análise guiada
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Vamos te guiar passo a passo. Apenas descreva um desafio 
                    do seu negócio e nossos agentes farão o resto.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex flex-col items-center gap-4">
              <button
                onClick={handleStartFirstAnalysis}
                className="flex items-center gap-2 px-8 py-4 bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-xl transition-all transform hover:scale-105"
              >
                <Sparkles className="w-5 h-5" />
                Iniciar Análise Guiada
              </button>
              <button
                onClick={handleNext}
                className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 text-sm"
              >
                Pular e explorar sozinho
              </button>
            </div>
          </WizardStep>

          {/* Step 4: Explore */}
          <WizardStep isActive={currentStep === 3}>
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-yellow-100 dark:bg-yellow-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🎉</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Tudo pronto!
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Você está configurado e pronto para começar
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 max-w-md mx-auto mb-8">
              {[
                { icon: '📊', title: 'Dashboard', desc: 'Acompanhe suas análises' },
                { icon: '➕', title: 'Nova Análise', desc: 'Crie análises rapidamente' },
                { icon: '📁', title: 'Histórico', desc: 'Acesse análises anteriores' },
                { icon: '⚙️', title: 'Configurações', desc: 'Personalize sua conta' },
              ].map((item) => (
                <div 
                  key={item.title}
                  className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl text-left"
                >
                  <span className="text-2xl mb-2 block">{item.icon}</span>
                  <h4 className="font-medium text-gray-900 dark:text-white">{item.title}</h4>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{item.desc}</p>
                </div>
              ))}
            </div>
          </WizardStep>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <button
            onClick={handleBack}
            disabled={currentStep === 0}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              currentStep === 0
                ? 'text-gray-300 dark:text-gray-600 cursor-not-allowed'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar
          </button>

          <div className="text-sm text-gray-500 dark:text-gray-400">
            {currentStep + 1} de {steps.length}
          </div>

          {currentStep < 2 && (
            <button
              onClick={handleNext}
              className="flex items-center gap-2 px-6 py-2 bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-lg transition-colors"
            >
              Continuar
              <ArrowRight className="w-4 h-4" />
            </button>
          )}

          {currentStep === 3 && (
            <button
              onClick={() => { completeOnboarding(); router.push('/dashboard'); }}
              className="flex items-center gap-2 px-6 py-2 bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-lg transition-colors"
            >
              Ir para Dashboard
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
