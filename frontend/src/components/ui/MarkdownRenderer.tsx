'use client';

import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { clsx } from 'clsx';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

/**
 * Pré-processa o conteúdo para formatar listas inline em listas Markdown
 * Converte padrões como "1) item 2) item 3) item" ou "1. item 2. item" em listas ordenadas
 */
function preprocessContent(content: string): string {
  if (!content) return '';
  
  let processed = content;
  
  // Padrão 1: "1) texto, 2) texto, 3) texto" ou "1) texto 2) texto 3) texto"
  // Detecta se há múltiplos itens numerados inline
  const inlineListPattern = /(\d+\))\s*([^,\d]+?)(?=\s*(?:\d+\)|$|,\s*\d+\)))/g;
  const matches = content.match(/\d+\)\s*[^,\d]+/g);
  
  if (matches && matches.length >= 2) {
    // Verifica se estão na mesma linha (não já formatados)
    const lines = content.split('\n');
    lines.forEach((line, index) => {
      const lineMatches = line.match(/(\d+)\)\s*([^,]+?)(?=\s*(?:\d+\)|$|,))/g);
      if (lineMatches && lineMatches.length >= 2) {
        // Encontrou lista inline, converter para lista Markdown
        let newLine = '\n';
        lineMatches.forEach((match) => {
          const itemMatch = match.match(/(\d+)\)\s*(.+)/);
          if (itemMatch) {
            const num = itemMatch[1];
            const text = itemMatch[2].trim().replace(/,\s*$/, '');
            newLine += `${num}. ${text}\n`;
          }
        });
        // Substitui a linha original pela lista formatada
        const textBefore = line.split(/\d+\)/)[0];
        lines[index] = textBefore.trim() + newLine;
      }
    });
    processed = lines.join('\n');
  }
  
  // Padrão 2: "- item - item - item" inline (bullets)
  const inlineBulletPattern = /(?:^|[.!?]\s+)([^-\n]*?)(-\s+[^-\n]+(?:\s+-\s+[^-\n]+)+)/gm;
  processed = processed.replace(inlineBulletPattern, (match, prefix, bullets) => {
    const items = bullets.split(/\s+-\s+/).filter(Boolean);
    if (items.length >= 2) {
      const bulletList = items.map((item: string) => `- ${item.trim()}`).join('\n');
      return `${prefix}\n\n${bulletList}`;
    }
    return match;
  });
  
  // Garante espaçamento adequado antes de títulos ##
  processed = processed.replace(/([^\n])(##\s)/g, '$1\n\n$2');
  
  // Garante que listas tenham linha em branco antes
  processed = processed.replace(/([^\n])\n(\d+\.\s)/g, '$1\n\n$2');
  processed = processed.replace(/([^\n])\n(-\s)/g, '$1\n\n$2');
  
  return processed;
}

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  const processedContent = useMemo(() => preprocessContent(content), [content]);
  
  return (
    <div
      className={clsx(
        'prose prose-slate dark:prose-invert max-w-none',
        // Headings
        'prose-headings:font-semibold prose-headings:tracking-tight',
        'prose-h1:text-2xl prose-h1:border-b prose-h1:border-gray-200 prose-h1:dark:border-gray-700 prose-h1:pb-3 prose-h1:mb-4',
        'prose-h2:text-xl prose-h2:mt-8 prose-h2:mb-4 prose-h2:text-primary',
        'prose-h3:text-lg prose-h3:mt-6 prose-h3:mb-3',
        // Paragraphs and text
        'prose-p:text-gray-700 prose-p:dark:text-gray-300 prose-p:leading-relaxed',
        'prose-strong:text-gray-900 prose-strong:dark:text-white prose-strong:font-semibold',
        // Lists
        'prose-ul:my-4 prose-ul:space-y-2',
        'prose-ol:my-4 prose-ol:space-y-2',
        'prose-li:text-gray-700 prose-li:dark:text-gray-300',
        'prose-li:marker:text-primary',
        // Links
        'prose-a:text-primary prose-a:no-underline prose-a:hover:underline',
        // Code
        'prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:bg-gray-100 prose-code:dark:bg-gray-800',
        'prose-code:text-sm prose-code:font-mono prose-code:text-primary',
        'prose-code:before:content-none prose-code:after:content-none',
        // Code blocks
        'prose-pre:bg-gray-900 prose-pre:dark:bg-gray-950 prose-pre:rounded-xl prose-pre:shadow-lg',
        'prose-pre:border prose-pre:border-gray-800',
        // Blockquotes
        'prose-blockquote:border-l-4 prose-blockquote:border-primary prose-blockquote:pl-4',
        'prose-blockquote:italic prose-blockquote:text-gray-600 prose-blockquote:dark:text-gray-400',
        'prose-blockquote:bg-gray-50 prose-blockquote:dark:bg-gray-800/50 prose-blockquote:py-2 prose-blockquote:pr-4 prose-blockquote:rounded-r-lg',
        // Tables
        'prose-table:border prose-table:border-gray-200 prose-table:dark:border-gray-700 prose-table:rounded-lg prose-table:overflow-hidden',
        'prose-th:bg-gray-100 prose-th:dark:bg-gray-800 prose-th:px-4 prose-th:py-2',
        'prose-td:px-4 prose-td:py-2 prose-td:border-t prose-td:border-gray-200 prose-td:dark:border-gray-700',
        // Horizontal rules
        'prose-hr:border-gray-200 prose-hr:dark:border-gray-700 prose-hr:my-8',
        className
      )}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {processedContent}
      </ReactMarkdown>
    </div>
  );
}

export default MarkdownRenderer;
