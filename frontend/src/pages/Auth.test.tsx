import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import Auth from "./Auth";

afterEach(() => vi.unstubAllGlobals());
it("requires organization name only for organizers", async () => {
  render(
    <MemoryRouter>
      <Auth register />
    </MemoryRouter>,
  );
  expect(
    screen.queryByLabelText("Название организации"),
  ).not.toBeInTheDocument();
  await userEvent.selectOptions(
    screen.getByLabelText("Ваша роль"),
    "ORGANIZER",
  );
  expect(screen.getByLabelText("Название организации")).toBeRequired();
});
it("reports failed login and re-enables submit", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ detail: "Неверный email или пароль" }),
    }),
  );
  render(
    <MemoryRouter>
      <Auth />
    </MemoryRouter>,
  );
  await userEvent.type(screen.getByLabelText("Email"), "volunteer@example.com");
  await userEvent.type(screen.getByLabelText("Пароль"), "incorrect");
  await userEvent.click(screen.getByRole("button", { name: "Войти" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Неверный email или пароль",
  );
  await waitFor(() =>
    expect(screen.getByRole("button", { name: "Войти" })).toBeEnabled(),
  );
});
