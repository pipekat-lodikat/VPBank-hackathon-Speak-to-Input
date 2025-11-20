import { useCallback, useEffect, useState } from 'react';
import AuthLogin, { type AuthMode } from './components/auth/AuthLogin';
import ChatPage from './pages/ChatPage';

type RoutePath = '/login' | '/register' | '/forgot-password' | '/chat';

const allowedRoutes: RoutePath[] = ['/login', '/register', '/forgot-password', '/chat'];

const authRouteForMode: Record<AuthMode, RoutePath> = {
  login: '/login',
  register: '/register',
  forgot: '/forgot-password',
};

const authModeForRoute: Record<RoutePath, AuthMode> = {
  '/login': 'login',
  '/register': 'register',
  '/forgot-password': 'forgot',
  '/chat': 'login',
};

const isRoute = (path: string): path is RoutePath =>
  allowedRoutes.includes(path as RoutePath);

const readStoredToken = () =>
  typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

const resolveInitialRoute = (hasToken: boolean): RoutePath => {
  if (typeof window === 'undefined') {
    return hasToken ? '/chat' : '/login';
  }

  const path = window.location.pathname;
  if (!isRoute(path)) {
    return hasToken ? '/chat' : '/login';
  }

  if (hasToken) {
    return '/chat';
  }

  if (!hasToken && path === '/chat') {
    return '/login';
  }

  return path as RoutePath;
};

function App() {
  const [accessToken, setAccessToken] = useState<string | null>(() => readStoredToken());
  const [route, setRoute] = useState<RoutePath>(() => resolveInitialRoute(Boolean(readStoredToken())));

  const navigate = useCallback(
    (path: RoutePath, { replace = false }: { replace?: boolean } = {}) => {
      if (typeof window !== 'undefined') {
        const currentPath = window.location.pathname as RoutePath;
        if (replace) {
          window.history.replaceState({}, '', path);
        } else if (currentPath !== path) {
          window.history.pushState({}, '', path);
        }
      }
      setRoute(path as RoutePath);
    },
    [],
  );

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handlePopState = () => {
      const path = window.location.pathname;

      if (!isRoute(path)) {
        navigate(accessToken ? '/chat' : '/login', { replace: true });
        return;
      }

      if (!accessToken && path === '/chat') {
        navigate('/login', { replace: true });
        return;
      }

      if (accessToken && path !== '/chat') {
        navigate('/chat', { replace: true });
        return;
      }

      setRoute(path);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [accessToken, navigate]);

  useEffect(() => {
    // Use queueMicrotask to defer navigation until after render
    if (accessToken && route !== '/chat') {
      queueMicrotask(() => navigate('/chat', { replace: true }));
    } else if (!accessToken && route === '/chat') {
      queueMicrotask(() => navigate('/login', { replace: true }));
    }
  }, [accessToken, route, navigate]);

  const handleLoginSuccess = (tokens: { access_token: string; id_token: string; refresh_token: string }) => {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('id_token', tokens.id_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    setAccessToken(tokens.access_token);
    navigate('/chat');
  };

  const handleSignOut = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('id_token');
    localStorage.removeItem('refresh_token');
    setAccessToken(null);
    navigate('/login');
  };

  const handleAuthModeChange = useCallback(
    (mode: AuthMode) => {
      navigate(authRouteForMode[mode]);
    },
    [navigate],
  );

  if (route === '/chat' && accessToken) {
    return <ChatPage accessToken={accessToken} onSignOut={handleSignOut} />;
  }

  const authMode = authModeForRoute[route] ?? 'login';

  return (
    <AuthLogin
      initialMode={authMode}
      onLoginSuccess={handleLoginSuccess}
      onChangeMode={handleAuthModeChange}
    />
  );
}

export default App;
