import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole, AuthResponse } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  role: UserRole | null;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (data: { email: string; password: string; full_name: string; role: string }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('knowbridge_token'));
  const [role, setRole] = useState<UserRole | null>((localStorage.getItem('knowbridge_role') as UserRole) || null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadUser() {
      if (token) {
        try {
          const profile = await api.getCurrentUser();
          setUser(profile);
          setRole(profile.role);
          localStorage.setItem('knowbridge_role', profile.role);
        } catch {
          // Token expired or invalid
          localStorage.removeItem('knowbridge_token');
          localStorage.removeItem('knowbridge_role');
          setToken(null);
          setUser(null);
          setRole(null);
        }
      }
      setIsLoading(false);
    }
    loadUser();
  }, [token]);

  const handleAuthSuccess = (res: AuthResponse) => {
    localStorage.setItem('knowbridge_token', res.access_token);
    localStorage.setItem('knowbridge_role', res.role);
    setToken(res.access_token);
    setRole(res.role);
    setUser({
      id: res.user_id,
      email: res.email,
      full_name: res.full_name,
      role: res.role,
      is_active: true,
      created_at: new Date().toISOString()
    });
  };

  const login = async (email: string, pass: string) => {
    const res = await api.login(email, pass);
    handleAuthSuccess(res);
  };

  const register = async (data: { email: string; password: string; full_name: string; role: string }) => {
    const res = await api.register(data);
    handleAuthSuccess(res);
  };

  const logout = () => {
    localStorage.removeItem('knowbridge_token');
    localStorage.removeItem('knowbridge_role');
    setToken(null);
    setUser(null);
    setRole(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, role, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
