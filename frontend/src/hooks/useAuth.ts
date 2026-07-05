'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface User {
  id: string;
  email: string;
  nombre: string;
  apellido?: string;
}

function setCookie(name: string, value: string) {
  document.cookie = `${name}=${value}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
}

function deleteCookie(name: string) {
  document.cookie = `${name}=; path=/; max-age=0`;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const savedUser = localStorage.getItem('thrivemind_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, refresh_token, user: userData } = response.data;

    localStorage.setItem('thrivemind_token', access_token);
    if (refresh_token) localStorage.setItem('thrivemind_refresh', refresh_token);
    localStorage.setItem('thrivemind_user', JSON.stringify(userData));
    setCookie('thrivemind_token', access_token);
    setUser(userData);

    router.push('/dashboard');
  };

  const register = async (email: string, password: string, nombre: string, apellido?: string) => {
    const response = await api.post('/auth/register', { email, password, nombre, apellido });
    const { access_token, refresh_token, user: userData } = response.data;

    localStorage.setItem('thrivemind_token', access_token);
    if (refresh_token) localStorage.setItem('thrivemind_refresh', refresh_token);
    localStorage.setItem('thrivemind_user', JSON.stringify(userData));
    setCookie('thrivemind_token', access_token);
    setUser(userData);

    router.push('/dashboard');
  };

  const logout = () => {
    localStorage.removeItem('thrivemind_token');
    localStorage.removeItem('thrivemind_refresh');
    localStorage.removeItem('thrivemind_user');
    deleteCookie('thrivemind_token');
    setUser(null);
    router.push('/login');
  };

  const isAuthenticated = !!user;

  return { user, loading, isAuthenticated, login, register, logout };
}
