export interface User {
  id: number;
  email: string;
  name: string;
  role: "VOLUNTEER" | "ORGANIZER";
  organization_name: string | null;
  city: string;
  description: string;
  skills: string;
  interests: string;
  website: string;
  avatar_url: string;
}
export type Organization = Pick<
  User,
  "id" | "organization_name" | "city" | "description" | "website" | "avatar_url"
>;
export interface Project {
  id: number;
  owner_id: number;
  title: string;
  city: string;
  location: string;
  starts_at: string;
  duration: number;
  duration_unit: string;
  description: string;
  category: string;
  cover_url: string;
  status: "DRAFT" | "PUBLISHED" | "ARCHIVED";
}
export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
export interface Session {
  user: User;
  csrf_token: string;
}
export const categories: Record<string, string> = {
  ANIMALS: "Помощь животным",
  ECOLOGY: "Экология",
  SOCIAL: "Социальная помощь",
  CULTURE: "Культура",
  EDUCATION: "Образование",
};
export const statuses: Record<string, string> = {
  DRAFT: "Черновик",
  PUBLISHED: "Опубликован",
  ARCHIVED: "В архиве",
};
export const units: Record<string, string> = {
  HOURS: "ч.",
  DAYS: "дн.",
  WEEKS: "нед.",
  MONTHS: "мес.",
};
