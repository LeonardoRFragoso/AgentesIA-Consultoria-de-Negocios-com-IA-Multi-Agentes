'use client';

import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import { motion, useInView, useScroll, useTransform } from 'framer-motion';
import { 
  ArrowRight, Brain, Users, TrendingUp, Shield, BarChart3, 
  MessageSquare, Sparkles, CheckCircle2, Play, Star, Zap,
  Target, Lightbulb, Clock, Award, ChevronDown,
  Quote, Building2, Rocket
} from 'lucide-react';

// Animation Variants
const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.1 } }
};

const slideInLeft = {
  hidden: { opacity: 0, x: -50 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } }
};

const slideInRight = {
  hidden: { opacity: 0, x: 50 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } }
};

// Floating particles component
function FloatingParticles() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {[...Array(15)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 bg-primary/20 rounded-full"
          animate={{
            y: [0, -20, 0],
            opacity: [0.2, 0.5, 0.2],
          }}
          transition={{
            duration: 4 + Math.random() * 4,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
        />
      ))}
    </div>
  );
}

// Animated counter component
function AnimatedCounter({ value, suffix = '' }: { value: number; suffix?: string }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (isInView) {
      let start = 0;
      const end = value;
      const duration = 2000;
      const increment = end / (duration / 16);
      const timer = setInterval(() => {
        start += increment;
        if (start >= end) {
          setCount(end);
          clearInterval(timer);
        } else {
          setCount(Math.floor(start));
        }
      }, 16);
      return () => clearInterval(timer);
    }
  }, [isInView, value]);

  return <span ref={ref}>{count.toLocaleString('pt-BR')}{suffix}</span>;
}

// Feature Card Component
function FeatureCard({ icon: Icon, title, description, gradient, index }: { 
  icon: React.ElementType; 
  title: string; 
  description: string;
  gradient: string;
  index: number;
}) {
  return (
    <motion.div 
      whileHover={{ y: -8, scale: 1.02 }}
      className="group relative bg-card border border-border rounded-2xl p-6 overflow-hidden hover:border-primary/50 transition-all duration-300 hover:shadow-xl hover:shadow-primary/10"
    >
      <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${gradient} opacity-10 rounded-full blur-2xl group-hover:opacity-20 transition-opacity`} />
      <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center mb-4 shadow-lg`}>
        <Icon className="h-7 w-7 text-white" />
      </div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </motion.div>
  );
}

export default function HomePage() {
  const [isScrolled, setIsScrolled] = useState(false);
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] });
  const heroOpacity = useTransform(scrollYProgress, [0, 1], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 1], [1, 0.95]);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      {/* Header */}
      <motion.header 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6 }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          isScrolled ? 'bg-background/80 backdrop-blur-xl shadow-lg border-b border-border/50' : 'bg-transparent'
        }`}
      >
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <motion.div className="flex items-center gap-2" whileHover={{ scale: 1.02 }}>
            <div className="relative">
              <Brain className="h-9 w-9 text-primary" />
              <motion.div 
                className="absolute inset-0 bg-primary/30 rounded-full blur-lg"
                animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </div>
            <span className="text-xl font-bold">AgentesIA</span>
          </motion.div>
          
          <nav className="hidden md:flex items-center gap-8">
            {['Recursos', 'Como Funciona', 'Preços', 'Depoimentos'].map((item, i) => (
              <motion.a
                key={item}
                href={`#${item.toLowerCase().replace(' ', '-')}`}
                className="text-muted-foreground hover:text-foreground transition-colors relative group"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 + 0.3 }}
              >
                {item}
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary transition-all duration-300 group-hover:w-full" />
              </motion.a>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <Link href="/login" className="text-muted-foreground hover:text-foreground transition-colors font-medium px-4 py-2">
              Entrar
            </Link>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Link href="/register" className="relative bg-primary text-primary-foreground px-5 py-2.5 rounded-full font-medium overflow-hidden group">
                <span className="relative z-10 flex items-center gap-2">
                  Cadastrar
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </span>
              </Link>
            </motion.div>
          </div>
        </div>
      </motion.header>

      {/* Hero Section */}
      <section ref={heroRef} className="relative min-h-screen flex items-center pt-20 overflow-hidden">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-primary/30 via-transparent to-transparent rounded-full blur-3xl animate-pulse" />
          <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-purple-500/20 via-transparent to-transparent rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        </div>
        <FloatingParticles />
        
        <motion.div style={{ opacity: heroOpacity, scale: heroScale }} className="container mx-auto px-4 py-20 relative z-10">
          <div className="text-center max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-8"
            >
              <Sparkles className="h-4 w-4" />
              <span>Powered by Claude AI da Anthropic</span>
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
            </motion.div>

            <motion.h1 
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-5xl md:text-7xl font-bold mb-6 leading-tight"
            >
              <span className="bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                Análise de Negócios
              </span>
              <br />
              <span className="bg-gradient-to-r from-primary via-blue-500 to-purple-500 bg-clip-text text-transparent">
                com Inteligência Artificial
              </span>
            </motion.h1>

            <motion.p 
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-3xl mx-auto"
            >
              Time de <strong className="text-foreground">5 agentes especializados</strong> que analisam seu negócio 
              sob múltiplas perspectivas: financeira, comercial, mercado e estratégica.
            </motion.p>

            <motion.div 
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="flex flex-col sm:flex-row gap-4 justify-center mb-12"
            >
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Link href="/register" className="group inline-flex items-center gap-2 bg-primary text-primary-foreground px-8 py-4 rounded-full text-lg font-semibold shadow-xl shadow-primary/25 hover:shadow-2xl transition-shadow">
                  <span>Começar Agora</span>
                  <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
                </Link>
              </motion.div>
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Link href="#como-funciona" className="group inline-flex items-center gap-2 bg-background border-2 border-border px-8 py-4 rounded-full text-lg font-semibold hover:border-primary/50 transition-all">
                  <Play className="h-5 w-5 text-primary" />
                  <span>Ver Como Funciona</span>
                </Link>
              </motion.div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-6 text-sm text-muted-foreground"
            >
              <div className="flex items-center gap-2">
                <div className="flex -space-x-2">
                  {['A', 'B', 'C', 'D'].map((letter, i) => (
                    <div key={i} className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-blue-600 border-2 border-background flex items-center justify-center text-white text-xs font-bold">
                      {letter}
                    </div>
                  ))}
                </div>
                <span>+500 empresas confiam</span>
              </div>
              <div className="hidden sm:block w-px h-6 bg-border" />
              <div className="flex items-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                ))}
                <span className="ml-1">4.9/5 de satisfação</span>
              </div>
            </motion.div>
          </div>

          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="absolute bottom-10 left-1/2 -translate-x-1/2"
          >
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="flex flex-col items-center gap-2 text-muted-foreground cursor-pointer"
            >
              <span className="text-sm">Saiba mais</span>
              <ChevronDown className="h-5 w-5" />
            </motion.div>
          </motion.div>
        </motion.div>
      </section>

      {/* Stats Section */}
      <section id="stats" className="py-20 bg-gradient-to-b from-background to-primary/5 relative">
        <div className="container mx-auto px-4">
          <motion.div 
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
            className="grid grid-cols-2 md:grid-cols-4 gap-8"
          >
            {[
              { value: 500, suffix: '+', label: 'Empresas Atendidas', icon: Building2 },
              { value: 15000, suffix: '+', label: 'Análises Realizadas', icon: BarChart3 },
              { value: 98, suffix: '%', label: 'Taxa de Satisfação', icon: Award },
              { value: 24, suffix: '/7', label: 'Disponibilidade', icon: Clock },
            ].map((stat, i) => (
              <motion.div key={i} variants={fadeInUp} className="text-center">
                <motion.div 
                  whileHover={{ scale: 1.05, y: -5 }}
                  className="bg-card border border-border/50 rounded-2xl p-6 shadow-lg hover:shadow-xl hover:border-primary/30 transition-all"
                >
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-primary/10 text-primary mb-4">
                    <stat.icon className="h-6 w-6" />
                  </div>
                  <div className="text-4xl font-bold bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent mb-2">
                    <AnimatedCounter value={stat.value} suffix={stat.suffix} />
                  </div>
                  <div className="text-muted-foreground font-medium">{stat.label}</div>
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* AI Consultant Feature */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-purple-500/5 to-blue-500/5" />
        <div className="container mx-auto px-4 relative">
          <motion.div 
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
            className="grid lg:grid-cols-2 gap-16 items-center"
          >
            <motion.div variants={slideInLeft}>
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-primary/20 to-purple-500/20 text-primary text-sm font-medium mb-6">
                <Sparkles className="h-4 w-4" />
                <span>Novo Recurso</span>
                <span className="px-2 py-0.5 bg-primary text-primary-foreground rounded-full text-xs">Beta</span>
              </div>
              
              <h2 className="text-4xl md:text-5xl font-bold mb-6 leading-tight">
                <span className="bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">Consultor IA</span>
                <br />
                <span className="bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">Contínuo</span>
              </h2>
              
              <p className="text-xl text-muted-foreground mb-8">
                Não pare na primeira análise. <strong className="text-foreground">Continue a conversa</strong> com a IA 
                para aprofundar pontos específicos e refinar suas estratégias.
              </p>
              
              <ul className="space-y-4 mb-8">
                {['A IA já conhece seu contexto e dados', 'Faça perguntas de follow-up ilimitadas', 'Exporte a análise + conversa completa', 'Histórico de conversas salvo'].map((item, i) => (
                  <motion.li key={i} variants={fadeInUp} className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center shadow-lg">
                      <CheckCircle2 className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-muted-foreground">{item}</span>
                  </motion.li>
                ))}
              </ul>
              
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Link href="/register" className="group inline-flex items-center gap-2 bg-gradient-to-r from-primary to-purple-500 text-white px-8 py-4 rounded-full font-semibold shadow-xl">
                  <span>Experimente Agora</span>
                  <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
                </Link>
              </motion.div>
            </motion.div>
            
            <motion.div variants={slideInRight} className="relative">
              <motion.div whileHover={{ y: -5 }} className="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between bg-gradient-to-r from-primary/5 to-purple-500/5">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <MessageSquare className="h-6 w-6 text-primary" />
                      <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white" />
                    </div>
                    <div>
                      <span className="font-semibold text-sm">Consultor IA</span>
                      <div className="flex items-center gap-1 text-xs text-green-500">
                        <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                        Online
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="p-6 space-y-4 bg-gray-50 dark:bg-gray-900/50 min-h-[280px]">
                  <motion.div initial={{ opacity: 0, x: 20 }} whileInView={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }} className="flex justify-end">
                    <div className="bg-gradient-to-r from-primary to-blue-600 text-white rounded-2xl rounded-br-md px-4 py-3 max-w-[80%] shadow-lg">
                      <p className="text-sm">Pode detalhar as ações de curto prazo para aumentar as vendas?</p>
                    </div>
                  </motion.div>
                  
                  <motion.div initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }} className="flex justify-start">
                    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-bl-md px-4 py-3 max-w-[85%] shadow-lg">
                      <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">Com base na análise, recomendo <strong>3 ações imediatas</strong>:</p>
                      <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                        {['Campanha de reativação de clientes', 'Revisão de precificação competitiva', 'Treinamento da equipe comercial'].map((item, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center text-xs font-bold">{i + 1}</span>
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </motion.div>
                </div>
                
                <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex gap-3 bg-white dark:bg-gray-800">
                  <div className="flex-1 bg-gray-100 dark:bg-gray-700 rounded-xl px-4 py-3 text-sm text-gray-400">
                    Faça uma pergunta...
                  </div>
                  <motion.button whileHover={{ scale: 1.05 }} className="w-12 h-12 bg-gradient-to-r from-primary to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                    <ArrowRight className="h-5 w-5 text-white" />
                  </motion.button>
                </div>
              </motion.div>
              
              <div className="absolute -top-8 -right-8 w-40 h-40 bg-gradient-to-br from-primary/20 to-purple-500/20 rounded-full blur-3xl" />
              <div className="absolute -bottom-8 -left-8 w-48 h-48 bg-gradient-to-tr from-blue-500/20 to-cyan-500/20 rounded-full blur-3xl" />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="recursos" className="py-24 relative">
        <div className="container mx-auto px-4">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer} className="text-center mb-16">
            <motion.div variants={fadeInUp} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
              <Zap className="h-4 w-4" />
              <span>Recursos Poderosos</span>
            </motion.div>
            <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-bold mb-6">
              Por que escolher <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">AgentesIA?</span>
            </motion.h2>
            <motion.p variants={fadeInUp} className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Combinamos o poder de 5 agentes especializados para uma análise completa do seu negócio.
            </motion.p>
          </motion.div>

          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer} className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: Users, title: 'Time de Especialistas', description: '5 agentes IA especializados: Analista, Comercial, Financeiro, Mercado e Revisor.', gradient: 'from-blue-500 to-cyan-500' },
              { icon: TrendingUp, title: 'Análise Profunda', description: 'Cada agente analisa seu problema sob perspectiva única, gerando insights complementares.', gradient: 'from-green-500 to-emerald-500' },
              { icon: BarChart3, title: 'Diagnóstico Executivo', description: 'Relatório consolidado com recomendações práticas e plano de ação prioritizado.', gradient: 'from-purple-500 to-pink-500' },
              { icon: MessageSquare, title: 'Consultor Contínuo', description: 'Continue a conversa após a análise para aprofundar pontos e esclarecer dúvidas.', gradient: 'from-orange-500 to-red-500' },
              { icon: Shield, title: 'Dados Seguros', description: 'Seus dados são processados de forma segura e nunca são compartilhados.', gradient: 'from-teal-500 to-blue-500' },
              { icon: Brain, title: 'IA de Ponta', description: 'Powered by Claude da Anthropic, um dos modelos de IA mais avançados do mundo.', gradient: 'from-indigo-500 to-purple-500' }
            ].map((feature, i) => (
              <motion.div key={i} variants={fadeInUp}>
                <FeatureCard {...feature} index={i} />
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* How it Works */}
      <section id="como-funciona" className="py-24 bg-gradient-to-b from-primary/5 to-background relative">
        <div className="container mx-auto px-4">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer} className="text-center mb-16">
            <motion.div variants={fadeInUp} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
              <Rocket className="h-4 w-4" />
              <span>Simples e Rápido</span>
            </motion.div>
            <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-bold mb-6">
              Como <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">funciona?</span>
            </motion.h2>
          </motion.div>

          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer} className="grid md:grid-cols-3 gap-8">
            {[
              { step: '01', title: 'Descreva seu Desafio', description: 'Conte para a IA qual é o problema ou oportunidade que você quer analisar.', icon: Lightbulb },
              { step: '02', title: 'Análise Multi-Agente', description: 'Nossos 5 agentes especializados analisam seu caso sob diferentes perspectivas.', icon: Brain },
              { step: '03', title: 'Receba seu Diagnóstico', description: 'Obtenha um relatório executivo com insights e plano de ação prioritizado.', icon: Target }
            ].map((item, i) => (
              <motion.div key={i} variants={fadeInUp}>
                <motion.div whileHover={{ y: -10 }} className="bg-card border border-border rounded-2xl p-8 text-center relative overflow-hidden group hover:border-primary/50 transition-all hover:shadow-xl">
                  <div className="absolute top-4 right-4 text-6xl font-bold text-primary/10 group-hover:text-primary/20 transition-colors">{item.step}</div>
                  <motion.div whileHover={{ rotate: 360 }} transition={{ duration: 0.5 }} className="relative z-10 w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center mx-auto mb-6 shadow-lg">
                    <item.icon className="h-8 w-8 text-white" />
                  </motion.div>
                  <h3 className="text-xl font-bold mb-3">{item.title}</h3>
                  <p className="text-muted-foreground">{item.description}</p>
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="depoimentos" className="py-24 relative">
        <div className="container mx-auto px-4">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer} className="text-center mb-16">
            <motion.div variants={fadeInUp} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
              <Star className="h-4 w-4" />
              <span>Depoimentos</span>
            </motion.div>
            <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-bold mb-6">
              O que nossos <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">clientes dizem</span>
            </motion.h2>
          </motion.div>

          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer} className="grid md:grid-cols-3 gap-6">
            {[
              { name: 'Carlos Silva', role: 'CEO, TechStart', content: 'A análise multi-agente revolucionou nossa tomada de decisão. Identificamos oportunidades que antes passavam despercebidas.', avatar: 'CS' },
              { name: 'Ana Beatriz', role: 'Diretora Financeira, Retail Plus', content: 'O consultor contínuo é incrível. Poder aprofundar a análise economizou semanas de consultoria tradicional.', avatar: 'AB' },
              { name: 'Roberto Mendes', role: 'Fundador, GrowthLab', content: 'A perspectiva do agente de mercado nos deu insights valiosos sobre nosso posicionamento. Recomendo!', avatar: 'RM' }
            ].map((testimonial, i) => (
              <motion.div key={i} variants={fadeInUp}>
                <motion.div whileHover={{ y: -5 }} className="bg-card border border-border rounded-2xl p-6 h-full relative hover:border-primary/30 transition-all hover:shadow-xl">
                  <Quote className="absolute top-4 right-4 h-12 w-12 text-primary/10" />
                  <div className="flex items-center gap-1 mb-4">
                    {[...Array(5)].map((_, j) => <Star key={j} className="h-4 w-4 fill-yellow-400 text-yellow-400" />)}
                  </div>
                  <p className="text-muted-foreground mb-6 italic">&ldquo;{testimonial.content}&rdquo;</p>
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center text-white font-bold">{testimonial.avatar}</div>
                    <div>
                      <div className="font-semibold">{testimonial.name}</div>
                      <div className="text-sm text-muted-foreground">{testimonial.role}</div>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Pricing */}
      <section id="preços" className="py-24 bg-gradient-to-b from-background to-primary/5 relative">
        <div className="container mx-auto px-4">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer} className="text-center mb-16">
            <motion.div variants={fadeInUp} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
              <Zap className="h-4 w-4" />
              <span>Planos Flexíveis</span>
            </motion.div>
            <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-bold mb-6">
              Escolha o plano <span className="bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">ideal</span>
            </motion.h2>
          </motion.div>

          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer} className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              { name: 'Gratuito', price: 'R$ 0', period: '/mês', description: 'Perfeito para experimentar', features: ['3 análises por mês', 'Diagnóstico executivo', 'Exportação PDF', 'Suporte por email'], cta: 'Começar Grátis', popular: false },
              { name: 'Profissional', price: 'R$ 97', period: '/mês', description: 'Para profissionais e PMEs', features: ['30 análises por mês', 'Consultor IA contínuo', 'Histórico completo', 'Exportação avançada', 'Suporte prioritário'], cta: 'Assinar Agora', popular: true },
              { name: 'Enterprise', price: 'Sob consulta', period: '', description: 'Para grandes empresas', features: ['Análises ilimitadas', 'API de integração', 'Treinamento dedicado', 'SLA garantido', 'Gerente de conta'], cta: 'Falar com Vendas', popular: false }
            ].map((plan, i) => (
              <motion.div key={i} variants={fadeInUp}>
                <motion.div whileHover={{ y: -10 }} className={`relative bg-card border rounded-2xl p-8 h-full ${plan.popular ? 'border-primary shadow-xl shadow-primary/10' : 'border-border'}`}>
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-primary to-blue-600 text-white text-sm font-medium rounded-full">
                      Mais Popular
                    </div>
                  )}
                  <div className="text-center mb-6">
                    <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
                    <p className="text-muted-foreground text-sm mb-4">{plan.description}</p>
                    <div className="text-4xl font-bold">
                      {plan.price}<span className="text-lg font-normal text-muted-foreground">{plan.period}</span>
                    </div>
                  </div>
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, j) => (
                      <li key={j} className="flex items-center gap-2 text-sm">
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Link href="/register" className={`block w-full py-3 rounded-full text-center font-semibold transition-all ${plan.popular ? 'bg-gradient-to-r from-primary to-blue-600 text-white shadow-lg' : 'border border-border hover:border-primary'}`}>
                      {plan.cta}
                    </Link>
                  </motion.div>
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary to-blue-600" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSIyIi8+PC9nPjwvZz48L3N2Zz4=')] opacity-30" />
        <div className="container mx-auto px-4 relative z-10">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={staggerContainer} className="text-center text-white max-w-3xl mx-auto">
            <motion.h2 variants={fadeInUp} className="text-4xl md:text-5xl font-bold mb-6">
              Pronto para transformar suas decisões de negócio?
            </motion.h2>
            <motion.p variants={fadeInUp} className="text-xl opacity-90 mb-10">
              Comece gratuitamente com 3 análises por mês. Sem cartão de crédito necessário.
            </motion.p>
            <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link href="/register" className="group inline-flex items-center gap-2 bg-white text-primary px-8 py-4 rounded-full text-lg font-semibold shadow-xl hover:shadow-2xl transition-all">
                  <span>Criar Conta Grátis</span>
                  <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
                </Link>
              </motion.div>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link href="#como-funciona" className="inline-flex items-center gap-2 border-2 border-white/50 text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-white/10 transition-all">
                  Saiba Mais
                </Link>
              </motion.div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 border-t border-border bg-background">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Brain className="h-8 w-8 text-primary" />
                <span className="text-xl font-bold">AgentesIA</span>
              </div>
              <p className="text-muted-foreground text-sm">
                Análise de negócios com inteligência artificial multi-agente. Transforme dados em decisões estratégicas.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Produto</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#recursos" className="hover:text-foreground transition-colors">Recursos</a></li>
                <li><a href="#como-funciona" className="hover:text-foreground transition-colors">Como Funciona</a></li>
                <li><a href="#preços" className="hover:text-foreground transition-colors">Preços</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Empresa</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Sobre</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Contato</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Privacidade</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Termos de Uso</a></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-border flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-muted-foreground">© 2024 AgentesIA. Todos os direitos reservados.</p>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>Powered by</span>
              <span className="font-semibold text-foreground">Claude AI</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
