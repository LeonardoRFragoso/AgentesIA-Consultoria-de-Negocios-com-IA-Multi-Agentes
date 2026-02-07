'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/services/api-client';
import { toast } from 'sonner';
import { 
  Brain, 
  ArrowLeft, 
  Loader2, 
  Building2, 
  FileText,
  Sparkles,
  Users,
  TrendingUp,
  DollarSign,
  Target,
  Zap,
  Clock,
  CheckCircle2,
  Upload,
  X,
  File,
  FileSpreadsheet,
  FileType
} from 'lucide-react';
import Link from 'next/link';

const BUSINESS_TYPES = [
  { value: 'SaaS', label: 'SaaS / Software', icon: Brain },
  { value: 'B2B', label: 'B2B / Empresas', icon: Building2 },
  { value: 'B2C', label: 'B2C / Consumidor', icon: Users },
  { value: 'E-commerce', label: 'E-commerce', icon: TrendingUp },
  { value: 'Serviços', label: 'Serviços', icon: Target },
  { value: 'Varejo', label: 'Varejo', icon: DollarSign },
];

const ANALYSIS_DEPTHS = [
  { value: 'Rápida', label: 'Rápida', description: '~2 min', detail: 'Visão geral rápida', icon: Zap },
  { value: 'Padrão', label: 'Padrão', description: '~5 min', detail: 'Análise completa', icon: Clock, recommended: true },
  { value: 'Profunda', label: 'Profunda', description: '~10 min', detail: 'Máximo detalhe', icon: Brain },
];

const ALLOWED_FILE_TYPES = [
  'text/csv',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/pdf',
  'text/plain',
];

const FILE_ICONS: Record<string, React.ElementType> = {
  'text/csv': FileSpreadsheet,
  'application/vnd.ms-excel': FileSpreadsheet,
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': FileSpreadsheet,
  'application/pdf': FileType,
  'text/plain': FileText,
};

export default function NovaAnalisePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [formData, setFormData] = useState({
    problem_description: '',
    business_type: 'SaaS',
    analysis_depth: 'Padrão',
  });

  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return;
    
    const validFiles = Array.from(selectedFiles).filter(file => {
      if (!ALLOWED_FILE_TYPES.includes(file.type)) {
        toast.error(`Tipo de arquivo não suportado: ${file.name}`);
        return false;
      }
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        toast.error(`Arquivo muito grande (máx 10MB): ${file.name}`);
        return false;
      }
      return true;
    });
    
    setFiles(prev => [...prev, ...validFiles].slice(0, 5)); // Max 5 files
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.problem_description.length < 50) {
      toast.error('Descreva o problema com mais detalhes (mínimo 50 caracteres)');
      return;
    }

    setIsLoading(true);
    
    // Feedback visual: Enviando pergunta
    toast.loading('📤 Enviando sua pergunta...', { id: 'analysis-submit' });

    try {
      // Usa endpoint com arquivos se houver arquivos anexados
      const result = files.length > 0 
        ? await apiClient.createAnalysisWithFiles({
            problem_description: formData.problem_description,
            business_type: formData.business_type,
            analysis_depth: formData.analysis_depth,
            files: files,
          })
        : await apiClient.createAnalysis({
            problem_description: formData.problem_description,
            business_type: formData.business_type,
            analysis_depth: formData.analysis_depth,
          });

      // Feedback visual: Análise iniciada
      toast.success('🚀 Análise iniciada! Redirecionando...', { id: 'analysis-submit' });
      
      // Pequeno delay para mostrar a mensagem
      setTimeout(() => {
        router.push(`/analise/${result.analysis_id || result.id}`);
      }, 500);
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Erro ao criar análise';
      toast.error(`❌ ${message}`, { id: 'analysis-submit' });
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-gray-50 to-primary/5 dark:from-gray-900 dark:via-gray-900 dark:to-gray-950">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link 
            href="/dashboard"
            className="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-primary transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Voltar ao Dashboard
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Title */}
        <div className="text-center mb-10">
          <div className="relative inline-flex">
            <div className="absolute inset-0 bg-primary/20 rounded-2xl blur-xl" />
            <div className="relative inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-blue-600 mb-4 shadow-lg">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white">
            Nova Análise Estratégica
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-3 max-w-lg mx-auto">
            Descreva seu problema de negócios e nosso time de 5 agentes especializados irá analisá-lo em detalhes
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Problem Description */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 lg:p-8 shadow-sm border border-gray-100 dark:border-gray-700">
            <div className="flex items-start gap-3 mb-4">
              <div className="p-2 rounded-xl bg-primary/10">
                <FileText className="w-5 h-5 text-primary" />
              </div>
              <div>
                <label className="block text-lg font-semibold text-gray-900 dark:text-white">
                  Descreva o problema ou oportunidade
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Seja específico: inclua contexto, números, timeframes e o que você já tentou
                </p>
              </div>
            </div>
            <textarea
              value={formData.problem_description}
              onChange={(e) => setFormData({ ...formData, problem_description: e.target.value })}
              placeholder="Ex: Nossas vendas caíram 20% nos últimos 3 meses. O principal canal de aquisição (Google Ads) aumentou o CPA em 45%. Temos 50 clientes ativos com MRR de R$150k. Qual pode ser a causa e como devemos responder?"
              rows={6}
              required
              className="w-full px-4 py-4 border border-gray-200 dark:border-gray-600 rounded-xl bg-gray-50 dark:bg-gray-700/50 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary focus:border-transparent focus:bg-white dark:focus:bg-gray-700 resize-none transition-all"
            />
            <div className="flex items-center justify-between mt-3">
              <p className="text-xs text-gray-400">
                {formData.problem_description.length} caracteres
              </p>
              <div className={`flex items-center gap-1.5 text-xs ${
                formData.problem_description.length >= 50 
                  ? 'text-emerald-500' 
                  : 'text-gray-400'
              }`}>
                <CheckCircle2 className="w-3.5 h-3.5" />
                {formData.problem_description.length >= 50 ? 'Mínimo atingido' : `Faltam ${50 - formData.problem_description.length} caracteres`}
              </div>
            </div>
          </div>

          {/* File Upload Section */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 lg:p-8 shadow-sm border border-gray-100 dark:border-gray-700">
            <div className="flex items-start gap-3 mb-4">
              <div className="p-2 rounded-xl bg-blue-500/10">
                <Upload className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <label className="block text-lg font-semibold text-gray-900 dark:text-white">
                  Anexar Arquivos (Opcional)
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Adicione planilhas, relatórios ou documentos para enriquecer a análise
                </p>
              </div>
            </div>
            
            {/* Drop Zone */}
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                isDragOver 
                  ? 'border-primary bg-primary/5 dark:bg-primary/10' 
                  : 'border-gray-200 dark:border-gray-600 hover:border-primary/50 hover:bg-gray-50 dark:hover:bg-gray-700/50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".csv,.xlsx,.xls,.pdf,.txt"
                onChange={(e) => handleFileSelect(e.target.files)}
                className="hidden"
              />
              <Upload className={`w-10 h-10 mx-auto mb-3 ${isDragOver ? 'text-primary' : 'text-gray-400'}`} />
              <p className="text-gray-700 dark:text-gray-300 font-medium">
                Arraste arquivos aqui ou clique para selecionar
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                CSV, Excel, PDF ou TXT (máx. 10MB cada, até 5 arquivos)
              </p>
            </div>
            
            {/* File List */}
            {files.length > 0 && (
              <div className="mt-4 space-y-2">
                {files.map((file, index) => {
                  const FileIcon = FILE_ICONS[file.type] || File;
                  return (
                    <div 
                      key={index}
                      className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
                    >
                      <div className="p-2 rounded-lg bg-blue-500/10">
                        <FileIcon className="w-5 h-5 text-blue-500" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={(e) => { e.stopPropagation(); removeFile(index); }}
                        className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Business Type */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 lg:p-8 shadow-sm border border-gray-100 dark:border-gray-700">
            <div className="flex items-start gap-3 mb-5">
              <div className="p-2 rounded-xl bg-emerald-500/10">
                <Building2 className="w-5 h-5 text-emerald-500" />
              </div>
              <label className="block text-lg font-semibold text-gray-900 dark:text-white">
                Tipo de Negócio
              </label>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {BUSINESS_TYPES.map((type) => {
                const Icon = type.icon;
                const isSelected = formData.business_type === type.value;
                return (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, business_type: type.value })}
                    className={`group p-4 rounded-xl border-2 transition-all text-left ${
                      isSelected
                        ? 'border-primary bg-primary/5 dark:bg-primary/10 shadow-lg shadow-primary/10'
                        : 'border-gray-200 dark:border-gray-700 hover:border-primary/50 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                    }`}
                  >
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 transition-colors ${
                      isSelected ? 'bg-primary/20' : 'bg-gray-100 dark:bg-gray-700 group-hover:bg-primary/10'
                    }`}>
                      <Icon className={`w-5 h-5 transition-colors ${isSelected ? 'text-primary' : 'text-gray-500 group-hover:text-primary'}`} />
                    </div>
                    <span className={`font-medium block transition-colors ${isSelected ? 'text-primary' : 'text-gray-700 dark:text-gray-300'}`}>
                      {type.label}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Analysis Depth */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 lg:p-8 shadow-sm border border-gray-100 dark:border-gray-700">
            <div className="flex items-start gap-3 mb-5">
              <div className="p-2 rounded-xl bg-purple-500/10">
                <Brain className="w-5 h-5 text-purple-500" />
              </div>
              <label className="block text-lg font-semibold text-gray-900 dark:text-white">
                Profundidade da Análise
              </label>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {ANALYSIS_DEPTHS.map((depth) => {
                const isSelected = formData.analysis_depth === depth.value;
                const Icon = depth.icon;
                return (
                  <button
                    key={depth.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, analysis_depth: depth.value })}
                    className={`relative group p-5 rounded-xl border-2 transition-all text-left ${
                      isSelected
                        ? 'border-primary bg-primary/5 dark:bg-primary/10 shadow-lg shadow-primary/10'
                        : 'border-gray-200 dark:border-gray-700 hover:border-primary/50 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                    }`}
                  >
                    {depth.recommended && (
                      <span className="absolute -top-2.5 left-4 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-primary text-white rounded-full">
                        Recomendado
                      </span>
                    )}
                    <div className="flex items-center gap-3 mb-2">
                      <Icon className={`w-5 h-5 transition-colors ${isSelected ? 'text-primary' : 'text-gray-400'}`} />
                      <span className={`font-semibold transition-colors ${isSelected ? 'text-primary' : 'text-gray-700 dark:text-gray-300'}`}>
                        {depth.label}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {depth.detail}
                    </p>
                    <p className={`text-xs mt-2 font-medium ${
                      isSelected ? 'text-primary' : 'text-gray-400'
                    }`}>
                      {depth.description}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Agents Preview */}
          <div className="bg-gradient-to-r from-primary/10 via-blue-500/10 to-purple-500/10 rounded-2xl p-6 lg:p-8 border border-primary/20">
            <div className="flex items-center gap-2 mb-4">
              <Users className="w-5 h-5 text-primary" />
              <h3 className="font-semibold text-gray-900 dark:text-white">
                Time de Agentes Especializados
              </h3>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Sua análise será processada por 5 agentes de IA com expertise complementar:
            </p>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur rounded-xl px-4 py-3 text-center border border-white/50 dark:border-gray-700">
                <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-blue-500/10 flex items-center justify-center">
                  <FileText className="w-5 h-5 text-blue-500" />
                </div>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Analista</span>
              </div>
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur rounded-xl px-4 py-3 text-center border border-white/50 dark:border-gray-700">
                <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                  <Target className="w-5 h-5 text-emerald-500" />
                </div>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Comercial</span>
              </div>
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur rounded-xl px-4 py-3 text-center border border-white/50 dark:border-gray-700">
                <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-amber-500/10 flex items-center justify-center">
                  <DollarSign className="w-5 h-5 text-amber-500" />
                </div>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Financeiro</span>
              </div>
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur rounded-xl px-4 py-3 text-center border border-white/50 dark:border-gray-700">
                <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-purple-500/10 flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-purple-500" />
                </div>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Mercado</span>
              </div>
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur rounded-xl px-4 py-3 text-center border border-white/50 dark:border-gray-700">
                <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-rose-500/10 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-rose-500" />
                </div>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Executivo</span>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading || formData.problem_description.length < 50}
            className="w-full py-4 px-6 bg-gradient-to-r from-primary to-blue-600 hover:from-primary/90 hover:to-blue-600/90 text-white font-semibold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-primary/25 hover:shadow-primary/40 disabled:shadow-none"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Iniciando análise...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                Iniciar Análise com IA
              </>
            )}
          </button>
        </form>
      </main>
    </div>
  );
}
