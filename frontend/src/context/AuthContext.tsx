"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import Cookies from "js-cookie";
import {
  User,
  AuthTokens,
  LoginCredentials,
  RegisterData,
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  getCurrentUser,
  refreshAccessToken,
} from "../lib/api";

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get tokens from cookies
  const getTokens = useCallback((): AuthTokens | null => {
    const access = Cookies.get(ACCESS_TOKEN_KEY);
    const refresh = Cookies.get(REFRESH_TOKEN_KEY);
    if (access && refresh) {
      return { access, refresh };
    }
    return null;
  }, []);

  // Save tokens to cookies
  const saveTokens = useCallback((tokens: AuthTokens) => {
    Cookies.set(ACCESS_TOKEN_KEY, tokens.access, { expires: 1 / 24 }); // 1 hour
    Cookies.set(REFRESH_TOKEN_KEY, tokens.refresh, { expires: 7 }); // 7 days
  }, []);

  // Clear tokens from cookies
  const clearTokens = useCallback(() => {
    Cookies.remove(ACCESS_TOKEN_KEY);
    Cookies.remove(REFRESH_TOKEN_KEY);
  }, []);

  // Fetch current user
  const fetchUser = useCallback(async (accessToken: string) => {
    try {
      const userData = await getCurrentUser(accessToken);
      setUser(userData);
    } catch {
      // Token might be expired, try to refresh
      const tokens = getTokens();
      if (tokens) {
        try {
          const newTokens = await refreshAccessToken(tokens.refresh);
          saveTokens(newTokens);
          const userData = await getCurrentUser(newTokens.access);
          setUser(userData);
        } catch {
          // Refresh failed, logout
          clearTokens();
          setUser(null);
        }
      } else {
        setUser(null);
      }
    }
  }, [getTokens, saveTokens, clearTokens]);

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const tokens = getTokens();
        if (tokens) {
          await fetchUser(tokens.access);
        }
      } catch (err) {
        console.error("Auth init error:", err);
        // Clear any invalid tokens
        clearTokens();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    initAuth();
  }, [getTokens, fetchUser, clearTokens]);

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      setError(null);
      setIsLoading(true);
      try {
        const response = await apiLogin(credentials);
        saveTokens(response.tokens);
        setUser(response.user);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Login failed";
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [saveTokens]
  );

  const register = useCallback(
    async (data: RegisterData) => {
      setError(null);
      setIsLoading(true);
      try {
        const response = await apiRegister(data);
        saveTokens(response.tokens);
        setUser(response.user);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Registration failed";
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [saveTokens]
  );

  const logout = useCallback(async () => {
    const tokens = getTokens();
    if (tokens) {
      try {
        await apiLogout(tokens.refresh);
      } catch {
        // Ignore logout errors, just clear local state
      }
    }
    clearTokens();
    setUser(null);
  }, [getTokens, clearTokens]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        error,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  // Return default values when not in provider (for SSR/build)
  if (context === undefined) {
    return {
      user: null,
      isAuthenticated: false,
      isLoading: true,
      login: async () => { throw new Error("Auth not initialized"); },
      register: async () => { throw new Error("Auth not initialized"); },
      logout: async () => { throw new Error("Auth not initialized"); },
      error: null,
    };
  }
  return context;
}
