'use client';

import Link from 'next/link';
import { ArrowRight, Brain, Users, TrendingUp, Shield, Zap, BarChart3, MessageSquare, Sparkles } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-8 w-8 text-primary" />
            <span className="text-xl font-bold">AgentesIA</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link 
              href="/login" 
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Entrar
            </Link>
            <Link
              href="/login"
              className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors"
            >
              Começar Grátis
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-4xl md:text-6xl font-bold mb-6 pb-2 bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
          Análise de Negócios com IA
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          Time de agentes especializados que analisam seu problema de negócio 
          sob múltiplas perspectivas: financeira, comercial, mercado e estratégica.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/login"
            className="bg-primary text-primary-foreground px-8 py-3 rounded-md text-lg font-medium hover:bg-primary/90 transition-colors flex items-center gap-2"
          >
            Começar Agora <ArrowRight className="h-5 w-5" />
          </Link>
          <Link
            href="#features"
            className="border border-border px-8 py-3 rounded-md text-lg font-medium hover:bg-accent transition-colors"
          >
            Saiba Mais
          </Link>
        </div>
      </section>

      {/* Destaque: Consultor IA Contínuo */}
      <section className="bg-gradient-to-r from-primary/5 via-purple-500/5 to-blue-500/5 py-20">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
                <Sparkles className="h-4 w-4" />
                Novo Recurso
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Consultor IA Contínuo
              </h2>
              <p className="text-lg text-muted-foreground mb-6">
                Não pare na primeira análise. <strong>Continue a conversa</strong> com a IA 
                para aprofundar pontos específicos, esclarecer dúvidas e refinar suas estratégias.
              </p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-muted-foreground">A IA já conhece seu contexto e dados</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-muted-foreground">Faça perguntas de follow-up ilimitadas (plano Enterprise)</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-muted-foreground">Exporte a análise + conversa completa</span>
                </li>
              </ul>
              <Link
                href="/login"
                className="bg-primary text-primary-foreground px-6 py-3 rounded-md font-medium hover:bg-primary/90 transition-colors inline-flex items-center gap-2"
              >
                Experimente Agora <ArrowRight className="h-5 w-5" />
              </Link>
            </div>
            <div className="relative">
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
                {/* Mock Chat Interface */}
                <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-primary" />
                  <span className="font-medium text-sm">Refinar Análise</span>
                </div>
                <div className="p-4 space-y-4 bg-gray-50 dark:bg-gray-900/50">
                  {/* User Message */}
                  <div className="flex justify-end">
                    <div className="bg-primary text-white rounded-2xl rounded-br-md px-4 py-2 max-w-[80%]">
                      <p className="text-sm">Pode detalhar as ações de curto prazo para aumentar as vendas?</p>
                    </div>
                  </div>
                  {/* AI Response */}
                  <div className="flex justify-start">
                    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-bl-md px-4 py-3 max-w-[85%]">
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        Com base na análise, recomendo 3 ações imediatas:
                      </p>
                      <ul className="text-sm text-gray-600 dark:text-gray-400 mt-2 space-y-1">
                        <li>• Campanha de reativação de clientes inativos</li>
                        <li>• Revisão de precificação competitiva</li>
                        <li>• Treinamento da equipe comercial</li>
                      </ul>
                    </div>
                  </div>
                </div>
                <div className="p-3 border-t border-gray-200 dark:border-gray-700 flex gap-2">
                  <div className="flex-1 bg-gray-100 dark:bg-gray-700 rounded-lg px-3 py-2 text-sm text-gray-400">
                    Faça uma pergunta...
                  </div>
                  <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                    <ArrowRight className="h-5 w-5 text-white" />
                  </div>
                </div>
              </div>
              {/* Decorative elements */}
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-primary/10 rounded-full blur-2xl"></div>
              <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">
          Por que usar AgentesIA?
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon={<Users className="h-10 w-10 text-primary" />}
            title="Time de Especialistas"
            description="5 agentes IA especializados: Analista, Comercial, Financeiro, Mercado e Revisor Executivo."
          />
          <FeatureCard
            icon={<TrendingUp className="h-10 w-10 text-primary" />}
            title="Análise Profunda"
            description="Cada agente analisa seu problema sob sua perspectiva única, gerando insights complementares."
          />
          <FeatureCard
            icon={<BarChart3 className="h-10 w-10 text-primary" />}
            title="Diagnóstico Executivo"
            description="Relatório consolidado com recomendações práticas e plano de ação prioritizado."
          />
          <FeatureCard
            icon={<MessageSquare className="h-10 w-10 text-primary" />}
            title="Consultor Contínuo"
            description="Continue a conversa após a análise para aprofundar pontos e esclarecer dúvidas."
          />
          <FeatureCard
            icon={<Shield className="h-10 w-10 text-primary" />}
            title="Dados Seguros"
            description="Seus dados são processados de forma segura e nunca são compartilhados."
          />
          <FeatureCard
            icon={<Brain className="h-10 w-10 text-primary" />}
            title="IA de Ponta"
            description="Powered by Claude da Anthropic, um dos modelos de IA mais avançados do mundo."
          />
        </div>
      </section>

      {/* CTA */}
      <section className="bg-primary/5 py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Pronto para transformar suas decisões?
          </h2>
          <p className="text-muted-foreground mb-8 max-w-xl mx-auto">
            Comece gratuitamente com 3 análises por mês. 
            Sem cartão de crédito necessário.
          </p>
          <Link
            href="/login"
            className="bg-primary text-primary-foreground px-8 py-3 rounded-md text-lg font-medium hover:bg-primary/90 transition-colors inline-flex items-center gap-2"
          >
            Criar Conta Grátis <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>© 2024 AgentesIA. Todos os direitos reservados.</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ 
  icon, 
  title, 
  description 
}: { 
  icon: React.ReactNode; 
  title: string; 
  description: string;
}) {
  return (
    <div className="p-6 rounded-lg border border-border bg-card hover:shadow-md transition-shadow">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
}
