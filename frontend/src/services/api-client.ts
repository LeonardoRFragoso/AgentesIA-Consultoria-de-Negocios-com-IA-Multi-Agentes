/**
 * API Client - Integração com Backend
 * 
 * Centraliza todas as chamadas HTTP com:
 * - Interceptors para auth token
 * - Refresh automático de token
 * - Error handling padronizado
 */

import axios, { AxiosError, AxiosInstance } from 'axios';
import Cookies from 'js-cookie';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Tokens cookies
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

class ApiClient {
  private client: AxiosInstance;
  private isRefreshing = false;
  private refreshQueue: Array<(token: string) => void> = [];

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api/v1`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - adiciona token
    this.client.interceptors.request.use(
      (config) => {
        const token = Cookies.get(ACCESS_TOKEN_KEY);
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - refresh token em 401
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && originalRequest) {
          if (this.isRefreshing) {
            // Aguarda refresh em andamento
            return new Promise((resolve) => {
              this.refreshQueue.push((token: string) => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                resolve(this.client(originalRequest));
              });
            });
          }

          this.isRefreshing = true;

          try {
            const refreshToken = Cookies.get(REFRESH_TOKEN_KEY);
            if (!refreshToken) {
              throw new Error('No refresh token');
            }

            const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
              refresh_token: refreshToken,
            });

            const { access_token, refresh_token } = response.data;

            // Salva novos tokens
            Cookies.set(ACCESS_TOKEN_KEY, access_token, { expires: 1 });
            Cookies.set(REFRESH_TOKEN_KEY, refresh_token, { expires: 30 });

            // Executa fila de requests pendentes
            this.refreshQueue.forEach((callback) => callback(access_token));
            this.refreshQueue = [];

            // Retry request original
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            // Refresh falhou - logout
            this.logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Auth methods
  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', { email, password });
    const { access_token, refresh_token } = response.data;

    Cookies.set(ACCESS_TOKEN_KEY, access_token, { expires: 1 });
    Cookies.set(REFRESH_TOKEN_KEY, refresh_token, { expires: 30 });

    return response.data;
  }

  async register(email: string, password: string, organizationName: string, name?: string) {
    const response = await this.client.post('/auth/register', {
      email,
      password,
      organization_name: organizationName,
      name,
    });

    const { access_token, refresh_token } = response.data;

    Cookies.set(ACCESS_TOKEN_KEY, access_token, { expires: 1 });
    Cookies.set(REFRESH_TOKEN_KEY, refresh_token, { expires: 30 });

    return response.data;
  }

  logout() {
    Cookies.remove(ACCESS_TOKEN_KEY);
    Cookies.remove(REFRESH_TOKEN_KEY);
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Analysis methods
  async createAnalysis(data: {
    problem_description: string;
    business_type?: string;
    analysis_depth?: string;
    use_cache?: boolean;
  }) {
    const response = await this.client.post('/async/analyses', data);
    return response.data;
  }

  async createAnalysisWithFiles(data: {
    problem_description: string;
    business_type?: string;
    analysis_depth?: string;
    files?: File[];
  }) {
    const formData = new FormData();
    formData.append('problem_description', data.problem_description);
    formData.append('business_type', data.business_type || 'SaaS');
    formData.append('analysis_depth', data.analysis_depth || 'Padrão');
    
    if (data.files) {
      data.files.forEach((file) => {
        formData.append('files', file);
      });
    }
    
    const response = await this.client.post('/async/analyses/with-files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getAnalysis(id: string) {
    const response = await this.client.get(`/async/analyses/${id}`);
    return response.data;
  }

  async getTaskStatus(taskId: string) {
    const response = await this.client.get(`/async/analyses/task/${taskId}`);
    return response.data;
  }

  async listAnalyses(params?: { limit?: number; offset?: number; status?: string }) {
    const response = await this.client.get('/async/analyses', { params });
    return response.data;
  }

  async deleteAnalysis(id: string) {
    await this.client.delete(`/async/analyses/${id}`);
  }

  // Generic request
  get<T>(url: string, params?: Record<string, unknown>) {
    return this.client.get<T>(url, { params });
  }

  post<T>(url: string, data?: Record<string, unknown>) {
    return this.client.post<T>(url, data);
  }

  put<T>(url: string, data?: Record<string, unknown>) {
    return this.client.put<T>(url, data);
  }

  delete<T>(url: string) {
    return this.client.delete<T>(url);
  }
}

export const apiClient = new ApiClient();
export default apiClient;
