import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, errorMessage } from "../api";
import { Feedback } from "../components";
import { useSession } from "../session";
import type { Session } from "../types";

export default function Auth({ register = false }: { register?: boolean }) {
  const [role, setRole] = useState("VOLUNTEER");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { accept } = useSession();
  const navigate = useNavigate();
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const credentials = {
      email: String(form.get("email")),
      password: String(form.get("password")),
    };
    try {
      if (register)
        await api("/auth/register", {
          method: "POST",
          body: JSON.stringify({
            ...credentials,
            name: form.get("name"),
            role,
            organization_name:
              role === "ORGANIZER" ? form.get("organization_name") : null,
          }),
        });
      accept(
        await api<Session>("/auth/login", {
          method: "POST",
          body: JSON.stringify(credentials),
        }),
      );
      navigate("/profile");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="auth-layout">
      <div className="auth-story">
        <h1>
          Присоединяйтесь!
        </h1>
      </div>
      <section className="panel">
        <h2>{register ? "Создать аккаунт" : "Войти"}</h2>
        <p className="muted">
          {register
            ? "Выберите, как вы хотите помогать."
            : "Войдите в свой личный кабинет."}
        </p>
        <form onSubmit={submit}>
          {register && (
            <>
              <label>
                Ваша роль
                <select value={role} onChange={(e) => setRole(e.target.value)}>
                  <option value="VOLUNTEER">Волонтёр</option>
                  <option value="ORGANIZER">Организатор</option>
                </select>
              </label>
              <label>
                Имя
                <input
                  name="name"
                  autoComplete="name"
                  required
                  maxLength={100}
                />
              </label>
              {role === "ORGANIZER" && (
                <label>
                  Название организации
                  <input name="organization_name" required maxLength={160} />
                </label>
              )}
            </>
          )}
          <label>
            Email
            <input
              name="email"
              type="email"
              autoComplete="email"
              required
              maxLength={254}
            />
          </label>
          <label>
            Пароль
            <input
              name="password"
              type="password"
              autoComplete={register ? "new-password" : "current-password"}
              minLength={register ? 10 : 1}
              maxLength={128}
              required
            />
          </label>
          {register && <small>Не менее 10 символов.</small>}
          <Feedback error={error} />
          <button disabled={busy}>
            {busy ? "Подождите…" : register ? "Зарегистрироваться" : "Войти"}
          </button>
        </form>
        <p className="muted">
          {register ? "Уже есть аккаунт?" : "Впервые здесь?"}{" "}
          <Link to={register ? "/login" : "/register"}>
            {register ? "Войти" : "Зарегистрироваться"}
          </Link>
        </p>
      </section>
    </div>
  );
}
