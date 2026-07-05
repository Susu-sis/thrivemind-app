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
    const { access_token, user: userData } = response.data;

    localStorage.setItem('thrivemind_token', access_token);
    localStorage.setItem('thrivemind_user', JSON.stringify(userData));
    setUser(userData);

    router.push('/dashboard');
  };

  const register = async (email: string, password: string, nombre: string, apellido?: string) => {
    const response = await api.post('/auth/register', { email, password, nombre, apellido });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('thrivemind_token', access_token);
    localStorage.setItem('thrivemind_user', JSON.stringify(userData));
    setUser(userData);

    router.push('/dashboard');
  };

  const logout = () => {
    localStorage.removeItem('thrivemind_token');
    localStorage.removeItem('thrivemind_user');
    setUser(null);
    router.push('/login');
  };

  const isAuthenticated = !!user;

  return { user, loading, isAuthenticated, login, register, logout };
}
