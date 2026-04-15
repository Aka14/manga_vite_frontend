import React from "react";
import { BASE_URL } from "../config/index";

const Card = ({
  manga_name,
  cover,
  current_chapter,
  chapter_url,
  latest_url,
  onRightClick,
}) => {
  console.log(manga_name, cover, current_chapter, chapter_url, latest_url);

  return (
    <div
      className="w-[200px] flex flex-col gap-.5 max-w-sm overflow-hidden mt-auto"
      onContextMenu={onRightClick}
    >
      <p className="font-bold text-xl">{manga_name}</p>
      <p className="text-md">{current_chapter}</p>
      <a
        href={`${BASE_URL + chapter_url}`}
        target="_blank"
        rel="noopener noreferrer"
        onClick={(e) => e.stopPropagation()}
      >
        <img
          className="h-85 rounded-2xl py-2 object-cover"
          src={cover}
          alt={`Cover image for ${manga_name}`}
        />
      </a>
    </div>
  );
};

export default Card;
