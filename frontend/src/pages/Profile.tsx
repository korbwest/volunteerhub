import { useState, type FormEvent } from "react";
import { Navigate, Link } from "react-router-dom";
import { api, errorMessage } from "../api";
import { Empty, Feedback } from "../components";
import { useSession } from "../session";
import type { User } from "../types";
import { Avatar } from "../Avatar";

export default function Profile() {
  const { user, loading, update } = useSession();
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);
  if (loading) return <Feedback loading />;
  if (!user) return <Navigate to="/login" replace />;
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSaved(false);
    setBusy(true);
    const values = Object.fromEntries(new FormData(event.currentTarget));
    try {
      update(
        await api<User>("/profile", {
          method: "PATCH",
          body: JSON.stringify(values),
        }),
      );
      setSaved(true);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <p className="eyebrow">ЛИЧНЫЙ КАБИНЕТ</p>
      <h1>Здравствуйте, {user.name}!</h1>
      <p className="muted">
        {user.role === "ORGANIZER" ? "Организатор" : "Волонтёр"} · {user.email}
      </p>
      <div className="detail-grid">
        <section className="panel">
          <Avatar
            src={user.avatar_url}
            name={
              user.role === "ORGANIZER"
                ? user.organization_name || user.name
                : user.name
            }
          />
          <h2>Мой профиль</h2>
          <form onSubmit={save}>
            <label>
              Имя
              <input
                name="name"
                defaultValue={user.name}
                required
                maxLength={100}
              />
            </label>
            {user.role === "ORGANIZER" && (
              <label>
                Название организации
                <input
                  name="organization_name"
                  defaultValue={user.organization_name || ""}
                  required
                  maxLength={160}
                />
              </label>
            )}
            <label>
              Город
              <input name="city" defaultValue={user.city} maxLength={100} />
            </label>
            <label>
              {user.role === "ORGANIZER" ? "Об организации" : "О себе"}
              <textarea
                name="description"
                defaultValue={user.description}
                maxLength={5000}
                rows={5}
              />
            </label>
            {user.role === "VOLUNTEER" && (
              <>
                <label>
                  Навыки
                  <input
                    name="skills"
                    defaultValue={user.skills}
                    maxLength={1000}
                  />
                </label>
                <label>
                  Интересы
                  <input
                    name="interests"
                    defaultValue={user.interests}
                    maxLength={1000}
                  />
                </label>
              </>
            )}
            <label>
              Ссылка на аватар
              <input
                type="url"
                name="avatar_url"
                defaultValue={user.avatar_url}
                maxLength={2000}
              />
            </label>
            <Feedback error={error} />
            {saved && (
              <p role="status" className="success">
                Профиль сохранён
              </p>
            )}
            <button disabled={busy}>
              {busy ? "Сохраняем…" : "Сохранить изменения"}
            </button>
          </form>
        </section>
        <aside>
          {user.role === "ORGANIZER" ? (
            <section className="panel">
              <h2>Ваши инициативы</h2>
              <p>Создавайте проекты и управляйте их публикацией.</p>
              <Link className="button" to="/manage">
                Мои проекты
              </Link>
            </section>
          ) : (
            <section className="panel">
              <h2>Мой вклад</h2>
              <Empty
                title="История участия пока пуста"
                text="Заявки, баллы, рейтинг и грейд появятся после подключения модуля участия."
              />
              <Link to="/">Найти проект</Link>
            </section>
          )}
        </aside>
      </div>
    </>
  );
}
