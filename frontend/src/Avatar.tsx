import { useState } from "react";

type AvatarProps = { src: string; name: string };

export function Avatar(props: AvatarProps) {
  return <AvatarImage key={props.src} {...props} />;
}

function AvatarImage({ src, name }: AvatarProps) {
  const [failed, setFailed] = useState(false);
  const label = `Аватар: ${name}`;
  if (!src || failed) {
    return (
      <span className="avatar avatar-placeholder" role="img" aria-label={label}>
        {name.trim().charAt(0).toLocaleUpperCase("ru-RU")}
      </span>
    );
  }
  return (
    <img
      className="avatar"
      src={src}
      alt={label}
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
    />
  );
}
