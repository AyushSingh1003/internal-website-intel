import axios from 'axios';
import { getToken, removeToken } from './auth';
import type { LoginRequest, LoginResponse, Scan, ScanListResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>('/auth/login', credentials);
  return response.data;
};

// Scan APIs
export const createScan = async (websiteUrl: string): Promise<Scan> => {
  const response = await api.post<Scan>('/scans/', { website_url: websiteUrl });
  return response.data;
};

export const getScans = async (page: number = 1, pageSize: number = 10): Promise<ScanListResponse> => {
  const response = await api.get<ScanListResponse>('/scans/', {
    params: { page, page_size: pageSize },
  });
  return response.data;
};

export const getScanById = async (id: number): Promise<Scan> => {
  const response = await api.get<Scan>(`/scans/${id}`);
  return response.data;
};

export const deleteScan = async (id: number): Promise<void> => {
  await api.delete(`/scans/${id}`);
};

export default api;