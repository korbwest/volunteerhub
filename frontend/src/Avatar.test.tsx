import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Avatar } from "./Avatar";

describe("Avatar", () => {
  it("renders the saved image URL", () => {
    render(<Avatar src="https://example.com/avatar.jpg" name="Анна" />);
    expect(screen.getByRole("img", { name: "Аватар: Анна" })).toHaveAttribute(
      "src",
      "https://example.com/avatar.jpg",
    );
  });

  it("shows a placeholder when no URL is saved", () => {
    render(<Avatar src="" name="Анна" />);
    expect(screen.getByRole("img", { name: "Аватар: Анна" }).tagName).toBe(
      "SPAN",
    );
  });

  it("falls back on failure and retries after the URL changes", () => {
    const { rerender } = render(
      <Avatar src="https://example.com/broken.jpg" name="Анна" />,
    );
    fireEvent.error(screen.getByRole("img"));
    expect(screen.getByRole("img").tagName).toBe("SPAN");
    rerender(<Avatar src="https://example.com/new.jpg" name="Анна" />);
    expect(screen.getByRole("img")).toHaveAttribute(
      "src",
      "https://example.com/new.jpg",
    );
  });
});
