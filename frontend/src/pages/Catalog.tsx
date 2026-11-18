import { useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import {
  categories,
  units,
  type Organization,
  type Page,
  type Project,
} from "../types";
import {
  Empty,
  Feedback,
  Pager,
  ProjectCard,
  useResource,
} from "../components";
import { useSession } from "../session";
import { Avatar } from "../Avatar";

export function Catalog({
  organizations = false,
}: {
  organizations?: boolean;
}) {
  const [filters, setFilters] = useState("");
  const [page, setPage] = useState(1);
  const path = organizations ? "/organizations" : "/projects";
  const { data, error, loading } = useResource<Page<Project | Organization>>(
    `${path}?page=${page}&${filters}`,
  );
  function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = new URLSearchParams();
    new FormData(event.currentTarget).forEach((value, key) => {
      if (String(value).trim()) query.set(key, String(value).trim());
    });
    setFilters(query.toString());
    setPage(1);
  }
  return (
    <>
      <form className="filters panel" onSubmit={search}>
        <label className="grow">
          Поиск
          <input
            name="search"
            placeholder={
              organizations
                ? "Название организации"
                : "Название или описание проекта"
            }
            maxLength={160}
          />
        </label>
        <label>
          Город
          <input name="city" placeholder="Все города" maxLength={100} />
        </label>
        {!organizations && (
          <>
            <label>
              Направление
              <select name="category">
                <option value="">Все направления</option>
                {Object.entries(categories).map(([key, name]) => (
                  <option key={key} value={key}>
                    {name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              С даты (UTC)
              <input name="date_from" type="date" />
            </label>
            <label>
              По дату (UTC)
              <input name="date_to" type="date" />
            </label>
          </>
        )}
        <button>Найти</button>
      </form>
      <div className="section-heading">
        <h2>{organizations ? "Организации" : "Доступные проекты"}</h2>
        {data && <span className="muted">Найдено: {data.total}</span>}
      </div>
      <Feedback error={error} loading={loading} />
      {data &&
        (data.items.length ? (
          <div className="grid">
            {data.items.map((item) =>
              organizations ? (
                <article key={item.id} className="panel org-card">
                  <Avatar
                    src={(item as Organization).avatar_url}
                    name={
                      (item as Organization).organization_name || "Организация"
                    }
                  />
                  <h2>
                    <Link to={`/organizations/${item.id}`}>
                      {(item as Organization).organization_name}
                    </Link>
                  </h2>
                  <p className="muted">{item.city || "Город не указан"}</p>
                  <p className="excerpt">
                    {item.description ||
                      "Организация ещё не добавила описание."}
                  </p>
                  <Link to={`/organizations/${item.id}`}>Об организации →</Link>
                </article>
              ) : (
                <ProjectCard key={item.id} project={item as Project} />
              ),
            )}
          </div>
        ) : (
          <Empty
            title="Пока ничего не найдено"
            text="Попробуйте изменить условия поиска или загляните позже."
          />
        ))}
      {data && <Pager page={page} total={data.total} onChange={setPage} />}
    </>
  );
}

export function ProjectDetail() {
  const { id } = useParams();
  const {
    data: project,
    error,
    loading,
  } = useResource<Project>(`/projects/${id}`);
  const { user } = useSession();
  return (
    <>
      <Link className="back" to="/">
        ← Все проекты
      </Link>
      <Feedback error={error} loading={loading} />
      {project && (
        <>
          <div className="detail-heading">
            <div>
              <span className="tag">{categories[project.category]}</span>
              <h1>{project.title}</h1>
              <p className="muted">
                {project.city} · {project.location}
              </p>
            </div>
            {user?.id === project.owner_id && (
              <Link className="button" to={`/manage/${id}`}>
                Управлять проектом
              </Link>
            )}
          </div>
          <div className="detail-grid">
            <article>
              <img
                className="cover"
                src={project.cover_url}
                alt="Обложка проекта"
                referrerPolicy="no-referrer"
              />
              <section className="panel">
                <h2>О проекте</h2>
                <p className="prewrap">{project.description}</p>
              </section>
            </article>
            <aside className="panel">
              <h2>Детали проекта</h2>
              <dl>
                <dt>Начало</dt>
                <dd>{new Date(project.starts_at).toLocaleString("ru-RU")}</dd>
                <dt>Продолжительность</dt>
                <dd>
                  {project.duration} {units[project.duration_unit]}
                </dd>
                <dt>Место</dt>
                <dd>{project.location}</dd>
              </dl>
              <Link to={`/organizations/${project.owner_id}`}>
                Об организаторе →
              </Link>
              <p className="notice">
                Подача заявок появится на следующем этапе развития сервиса.
              </p>
            </aside>
          </div>
        </>
      )}
    </>
  );
}

export function OrganizationDetail() {
  const { id } = useParams();
  const { data, error, loading } = useResource<Organization>(
    `/organizations/${id}`,
  );
  const [page, setPage] = useState(1);
  const projects = useResource<Page<Project>>(
    `/projects?organization_id=${id}&page=${page}`,
  );
  return (
    <>
      <Link className="back" to="/organizations">
        ← Все организации
      </Link>
      <Feedback error={error} loading={loading} />
      {data && (
        <>
          <section className="panel organization-detail">
            <Avatar
              src={data.avatar_url}
              name={data.organization_name || "Организация"}
            />
            <p className="eyebrow">ОРГАНИЗАЦИЯ</p>
            <h1>{data.organization_name}</h1>
            <p className="muted">{data.city}</p>
            <p className="prewrap">
              {data.description || "Описание пока не добавлено."}
            </p>
            {data.website && (
              <a href={data.website} target="_blank" rel="noreferrer">
                Сайт организации ↗
              </a>
            )}
          </section>
          <h2>Проекты организации</h2>
          <Feedback error={projects.error} loading={projects.loading} />
          {projects.data &&
            (projects.data.items.length ? (
              <div className="grid">
                {projects.data.items.map((project) => (
                  <ProjectCard key={project.id} project={project} />
                ))}
              </div>
            ) : (
              <Empty
                title="Проектов пока нет"
                text="Здесь появятся опубликованные проекты организации."
              />
            ))}
          {projects.data && (
            <Pager page={page} total={projects.data.total} onChange={setPage} />
          )}
        </>
      )}
    </>
  );
}
