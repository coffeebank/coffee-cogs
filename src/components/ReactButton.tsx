import React from 'react';
import { Link } from 'gatsby';

interface Props {
  children: React.ReactNode,
  body: string,
  classButton: string,
  className: string,
  newTab: boolean,
  to: string,
}

export default function ReactButton({
    children,
    body = "Open Link",
    classButton = "bg-purple-700/90 hover:bg-purple-800/90 dark:bg-purple-800/90 dark:hover:bg-purple-700/90 text-white",
    className = "",
    newTab = true,
    to
  }: Props) {
  return (
    <div className={ "mb-[24px] " + className }>
      <Link to={ to } target={ newTab === true ? "_blank" : "" } rel="noopener noreferrer" className="!no-underline inline-block">
        { children ? (
          children
        ) : (
          <div className={ "px-6 py-3 transition duration-300 rounded-md !no-underline " + classButton }>
            { body }
          </div>
        )}
      </Link>
    </div>
  );
}
