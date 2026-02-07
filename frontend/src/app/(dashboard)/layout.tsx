'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import Link from 'next/link';
import { 
  Brain, 
  LayoutDashboard, 
  FileText, 
  CreditCard, 
  Settings, 
  LogOut,
  Menu,
  X,
  Sparkles,
  ChevronRight,
  Plus
} from 'lucide-react';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, logout, fetchUser } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isActive = (href: string) => {
    if (href === '/dashboard') return pathname === '/dashboard';
    return pathname?.startsWith(href);
  };

  useEffect(() => {
    // Tenta buscar usuário se não estiver autenticado
    if (!isAuthenticated) {
      fetchUser().catch(() => {
        router.push('/login');
      });
    }
  }, [isAuthenticated, fetchUser, router]);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Nova Análise', href: '/nova-analise', icon: FileText },
    { name: 'Faturamento', href: '/billing', icon: CreditCard },
  ];

  // Loading state
  if (!isAuthenticated && !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-pulse flex flex-col items-center">
          <Brain className="w-12 h-12 text-primary mb-4" />
          <p className="text-gray-500">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-full w-64 
        bg-gradient-to-b from-gray-900 via-gray-900 to-gray-950
        transform transition-transform duration-300 ease-out
        lg:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between px-5 py-6">
            <Link href="/dashboard" className="flex items-center gap-3 group">
              <div className="relative">
                <div className="absolute inset-0 bg-primary/20 rounded-xl blur-lg group-hover:bg-primary/30 transition-colors" />
                <div className="relative w-10 h-10 bg-gradient-to-br from-primary to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                  <Brain className="w-6 h-6 text-white" />
                </div>
              </div>
              <div>
                <span className="font-bold text-lg text-white">AgentesIA</span>
                <span className="block text-[10px] text-gray-500 uppercase tracking-wider">Business Intelligence</span>
              </div>
            </Link>
            <button 
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-800 text-gray-400"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Quick Action */}
          <div className="px-4 mb-4">
            <Link
              href="/nova-analise"
              className="flex items-center justify-center gap-2 w-full px-4 py-3 bg-gradient-to-r from-primary to-blue-600 hover:from-primary/90 hover:to-blue-600/90 text-white rounded-xl font-medium transition-all shadow-lg shadow-primary/25 hover:shadow-primary/40"
            >
              <Plus className="w-5 h-5" />
              Nova Análise
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-2 space-y-1">
            <p className="px-3 mb-2 text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Menu</p>
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group ${
                    active 
                      ? 'bg-primary/10 text-primary' 
                      : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'
                  }`}
                >
                  <div className={`p-1.5 rounded-lg transition-colors ${
                    active ? 'bg-primary/20' : 'bg-gray-800 group-hover:bg-gray-700'
                  }`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="font-medium">{item.name}</span>
                  {active && <ChevronRight className="w-4 h-4 ml-auto" />}
                </Link>
              );
            })}
          </nav>

          {/* Pro Badge */}
          <div className="px-4 mb-4">
            <div className="p-4 rounded-xl bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700/50">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">
                  {user?.organization?.plan?.toUpperCase() || 'FREE'}
                </span>
              </div>
              <p className="text-xs text-gray-400 mb-3">
                {user?.organization?.plan === 'free' 
                  ? 'Upgrade para desbloquear mais recursos'
                  : 'Acesso completo a todos os recursos'
                }
              </p>
              {user?.organization?.plan === 'free' && (
                <Link
                  href="/billing"
                  className="block w-full text-center px-3 py-2 text-xs font-medium text-white bg-gradient-to-r from-amber-500 to-orange-500 rounded-lg hover:from-amber-600 hover:to-orange-600 transition-all"
                >
                  Fazer Upgrade
                </Link>
              )}
            </div>
          </div>

          {/* User section */}
          <div className="border-t border-gray-800 p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/20 to-blue-600/20 flex items-center justify-center ring-2 ring-gray-700">
                <span className="text-primary font-semibold">
                  {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user?.name || user?.email}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {user?.organization?.name || 'Minha Empresa'}
                </p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 w-full px-3 py-2.5 text-sm text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all"
            >
              <LogOut className="w-4 h-4" />
              Sair da conta
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Mobile header */}
        <header className="lg:hidden sticky top-0 z-30 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between px-4 py-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <Menu className="w-6 h-6" />
            </button>
            <Link href="/dashboard" className="flex items-center gap-2">
              <Brain className="w-6 h-6 text-primary" />
              <span className="font-bold">AgentesIA</span>
            </Link>
            <div className="w-10" /> {/* Spacer */}
          </div>
        </header>

        {/* Page content */}
        <main>{children}</main>
      </div>
    </div>
  );
}
