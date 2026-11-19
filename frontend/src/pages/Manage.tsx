import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";
import { api, errorMessage } from "../api";
import { Empty, Feedback, Pager, useResource } from "../components";
import { useSession } from "../session";
import { categories, statuses, units, type Page, type Project } from "../types";

export function Manage() {
  const { user, loading } = useSession();
  if (loading) return <Feedback loading />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== "ORGANIZER") return <Navigate to="/" replace />;
  return <ManageList />;
}
function ManageList() {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");
  const { data, error, loading } = useResource<Page<Project>>(
    `/my/projects?page=${page}${status ? `&status=${status}` : ""}`,
  );
  return (
    <>
      <div className="section-heading">
        <div>
          <p className="eyebrow">КАБИНЕТ ОРГАНИЗАТОРА</p>
          <h1>Мои проекты</h1>
        </div>
        <Link className="button" to="/manage/new">
          + Создать проект
        </Link>
      </div>
      <div className="section-heading">
        <label>
          Статус
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
          >
            <option value="">Все статусы</option>
            {Object.entries(statuses).map(([key, title]) => (
              <option key={key} value={key}>
                {title}
              </option>
            ))}
          </select>
        </label>
        {data && (
          <p>
            Проектов: <strong>{data.total}</strong>
          </p>
        )}
      </div>
      <Feedback error={error} loading={loading} />
      {data &&
        (data.items.length ? (
          <div className="project-list">
            {data.items.map((project) => (
              <article className="panel manage-row" key={project.id}>
                <div>
                  <span className="tag">{statuses[project.status]}</span>
                  <h2>
                    <Link to={`/manage/${project.id}`}>{project.title}</Link>
                  </h2>
                  <p className="muted">
                    {project.city} ·{" "}
                    {new Date(project.starts_at).toLocaleDateString("ru-RU")}
                  </p>
                </div>
                <Link to={`/manage/${project.id}`}>Открыть</Link>
              </article>
            ))}
          </div>
        ) : (
          <Empty
            title="Здесь будут ваши проекты"
            text="Создайте первую инициативу. Она сохранится как черновик."
          />
        ))}
      {data && <Pager page={page} total={data.total} onChange={setPage} />}
    </>
  );
}

export function Editor() {
  const { id } = useParams();
  const { user, loading } = useSession();
  if (loading) return <Feedback loading />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== "ORGANIZER") return <Navigate to="/" replace />;
  return id ? (
    <ExistingEditor id={id} userId={user.id} />
  ) : (
    <ProjectForm key="new" />
  );
}
function ExistingEditor({ id, userId }: { id: string; userId: number }) {
  const { data, loading, error } = useResource<Project>(`/projects/${id}`);
  if (data && data.owner_id !== userId)
    return <p role="alert">Этот проект принадлежит другой организации.</p>;
  return (
    <>
      <Feedback loading={loading} error={error} />
      {data && <ProjectForm key={data.id} project={data} />}
    </>
  );
}
function localDate(value: string) {
  const date = new Date(value);
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
}
function ProjectForm({ project }: { project?: Project }) {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [current, setCurrent] = useState(project);
  const [saved, setSaved] = useState(false);
  const archived = current?.status === "ARCHIVED";
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setSaved(false);
    const values = Object.fromEntries(new FormData(event.currentTarget));
    try {
      const result = await api<Project>(
        current ? `/projects/${current.id}` : "/projects",
        {
          method: current ? "PATCH" : "POST",
          body: JSON.stringify({
            ...values,
            duration: Number(values.duration),
            starts_at: new Date(String(values.starts_at)).toISOString(),
          }),
        },
      );
      setCurrent(result);
      setSaved(true);
      if (!current) navigate(`/manage/${result.id}`, { replace: true });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }
  async function transition(status: string) {
    if (!current) return;
    if (
      status === "ARCHIVED" &&
      !window.confirm(
        "Архивировать проект? Его нельзя будет редактировать или опубликовать снова.",
      )
    )
      return;
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      setCurrent(
        await api<Project>(`/projects/${current.id}/status`, {
          method: "POST",
          body: JSON.stringify({ status }),
        }),
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Link className="back" to="/manage">
        Мои проекты
      </Link>
      <h1>{current ? current.title : "Новый проект"}</h1>
      {current && <span className="tag">{statuses[current.status]}</span>}
      <div className="editor-layout">
        <section className="panel">
          <form onSubmit={save}>
            <fieldset disabled={busy || archived}>
              <label>
                Название
                <input
                  name="title"
                  defaultValue={current?.title}
                  required
                  maxLength={160}
                />
              </label>
              <div className="form-row">
                <label>
                  Город
                  <input
                    name="city"
                    defaultValue={current?.city}
                    required
                    maxLength={100}
                  />
                </label>
                <label>
                  Локация
                  <input
                    name="location"
                    defaultValue={current?.location}
                    required
                    maxLength={300}
                  />
                </label>
              </div>
              <label>
                Дата и время начала (ваш часовой пояс)
                <input
                  name="starts_at"
                  type="datetime-local"
                  defaultValue={current ? localDate(current.starts_at) : ""}
                  required
                />
              </label>
              <div className="form-row">
                <label>
                  Продолжительность
                  <input
                    name="duration"
                    type="number"
                    min={1}
                    max={10000}
                    defaultValue={current?.duration || 1}
                    required
                  />
                </label>
                <label>
                  Единица
                  <select
                    name="duration_unit"
                    defaultValue={current?.duration_unit || "HOURS"}
                  >
                    {Object.entries(units).map(([key, title]) => (
                      <option key={key} value={key}>
                        {title}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
              <label>
                Направление
                <select
                  name="category"
                  defaultValue={current?.category || "SOCIAL"}
                >
                  {Object.entries(categories).map(([key, title]) => (
                    <option key={key} value={key}>
                      {title}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Описание
                <textarea
                  name="description"
                  rows={7}
                  defaultValue={current?.description}
                  required
                  maxLength={10000}
                />
              </label>
              <label>
                Ссылка на обложку
                <input
                  type="url"
                  name="cover_url"
                  defaultValue={current?.cover_url}
                  required
                  maxLength={2000}
                  placeholder="https://…"
                />
              </label>
              {!archived && (
                <button type="submit">
                  {busy
                    ? "Сохраняем…"
                    : current
                      ? "Сохранить изменения"
                      : "Сохранить черновик"}
                </button>
              )}
            </fieldset>
            <Feedback error={error} />
            {saved && (
              <p className="success" role="status">
                Изменения сохранены
              </p>
            )}
          </form>
        </section>
        <aside className="panel">
          <h2>Публикация</h2>
          <p>
            {archived
              ? "Проект сохранён в архиве. Изменения больше недоступны."
              : "Сначала сохраните изменения, затем публикуйте проект. Черновики видны только вам."}
          </p>
          {current && !archived && (
            <div className="actions">
              <button
                disabled={busy}
                onClick={() =>
                  transition(current.status === "DRAFT" ? "PUBLISHED" : "DRAFT")
                }
              >
                {current.status === "DRAFT"
                  ? "Опубликовать"
                  : "Вернуть в черновики"}
              </button>
              <button
                className="danger"
                disabled={busy}
                onClick={() => transition("ARCHIVED")}
              >
                Архивировать
              </button>
            </div>
          )}
          {current && (
            <Link to={`/projects/${current.id}`}>Посмотреть карточку</Link>
          )}
        </aside>
      </div>
    </>
  );
}
