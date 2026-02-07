'use client';

import React from 'react';
import { clsx } from 'clsx';
import { LucideIcon } from 'lucide-react';

interface Tab {
  id: string;
  label: string;
  icon?: LucideIcon;
  badge?: string | number;
}

interface TabsProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  variant?: 'underline' | 'pills' | 'cards';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Tabs({
  tabs,
  activeTab,
  onTabChange,
  variant = 'underline',
  size = 'md',
  className,
}: TabsProps) {
  const sizeStyles = {
    sm: 'px-3 py-2 text-xs',
    md: 'px-4 py-3 text-sm',
    lg: 'px-6 py-4 text-base',
  };

  const variantStyles = {
    underline: {
      container: 'border-b border-gray-200 dark:border-gray-700',
      tab: (isActive: boolean) =>
        clsx(
          'relative font-medium transition-colors whitespace-nowrap',
          sizeStyles[size],
          isActive
            ? 'text-primary'
            : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
        ),
      indicator: 'absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-t-full',
    },
    pills: {
      container: 'bg-gray-100 dark:bg-gray-800 p-1 rounded-xl',
      tab: (isActive: boolean) =>
        clsx(
          'font-medium transition-all whitespace-nowrap rounded-lg',
          sizeStyles[size],
          isActive
            ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
            : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
        ),
      indicator: '',
    },
    cards: {
      container: 'flex gap-2',
      tab: (isActive: boolean) =>
        clsx(
          'font-medium transition-all whitespace-nowrap rounded-xl border-2',
          sizeStyles[size],
          isActive
            ? 'border-primary bg-primary/5 text-primary'
            : 'border-transparent bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600'
        ),
      indicator: '',
    },
  };

  const styles = variantStyles[variant];

  return (
    <div className={clsx('flex overflow-x-auto scrollbar-hide', styles.container, className)}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        const Icon = tab.icon;

        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={clsx(styles.tab(isActive), 'flex items-center gap-2')}
          >
            {Icon && <Icon className="w-4 h-4" />}
            <span>{tab.label}</span>
            {tab.badge !== undefined && (
              <span
                className={clsx(
                  'px-1.5 py-0.5 text-xs rounded-full',
                  isActive
                    ? 'bg-primary/20 text-primary'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                )}
              >
                {tab.badge}
              </span>
            )}
            {variant === 'underline' && isActive && <span className={styles.indicator} />}
          </button>
        );
      })}
    </div>
  );
}

export default Tabs;
