/**
 * Auth Store - Estado global de autenticação
 * 
 * Usa Zustand para gerenciamento de estado simples e performático.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from '@/services/api-client';

export interface User {
  id: string;
  email: string;
  name: string | null;
  role: string;
  org_id: string;
  organization: {
    id: string;
    name: string;
    plan: string;
  };
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, orgName: string, name?: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: false,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          await apiClient.login(email, password);
          await get().fetchUser();
        } finally {
          set({ isLoading: false });
        }
      },

      register: async (email: string, password: string, orgName: string, name?: string) => {
        set({ isLoading: true });
        try {
          await apiClient.register(email, password, orgName, name);
          await get().fetchUser();
        } finally {
          set({ isLoading: false });
        }
      },

      logout: () => {
        apiClient.logout();
        set({ user: null, isAuthenticated: false });
      },

      fetchUser: async () => {
        try {
          const user = await apiClient.getCurrentUser();
          set({ user, isAuthenticated: true });
        } catch {
          set({ user: null, isAuthenticated: false });
        }
      },

      setUser: (user: User | null) => {
        set({ user, isAuthenticated: !!user });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
