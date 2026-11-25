import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { api, ApiError, setCsrf } from "./api";
import type { Session, User } from "./types";

const Context = createContext<{
  user: User | null;
  loading: boolean;
  accept: (value: Session) => void;
  update: (user: User) => void;
  logout: () => Promise<void>;
}>({
  user: null,
  loading: true,
  accept: () => {},
  update: () => {},
  logout: async () => {},
});
export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  function accept(session: Session) {
    setUser(session.user);
    setCsrf(session.csrf_token);
  }
  useEffect(() => {
    let active = true;
    const expire = () => {
      setUser(null);
      setCsrf("");
    };
    window.addEventListener("session-expired", expire);
    api<Session>("/auth/me")
      .then((session) => {
        if (active) accept(session);
      })
      .catch(() => {
        if (active) {
          setUser(null);
          setCsrf("");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
      window.removeEventListener("session-expired", expire);
    };
  }, []);
  async function logout() {
    try {
      await api("/auth/logout", { method: "POST" });
    } catch (error) {
      if (!(error instanceof ApiError && error.status === 401)) throw error;
    }
    setUser(null);
    setCsrf("");
  }
  return (
    <Context.Provider
      value={{ user, loading, accept, update: setUser, logout }}
    >
      {children}
    </Context.Provider>
  );
}
export function useSession() {
  return useContext(Context);
}
