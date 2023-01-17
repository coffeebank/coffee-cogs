import React from 'react';

interface Props {
  height?: number,
  title?: string,
  to: string,
  newTab?: boolean,
}

export const Head = ({ height = 400 }: Props) => (
  <>
    <style>
      {`
        .components-reactframe__height {
          height: ${ height };
        }
      `}
    </style>
  </>
)

export default function ReactFrame({ newTab = true, title, to }: Props) {
  return (
    <div className="w-full rounded-lg overflow-hidden components-reactframe__height">
      <iframe
        src={ to }
        className="w-full border-0 components-reactframe__height"
        title={ title || to }
      >
        <a href={ to } target={ newTab === true ? "_blank" : "" } rel="noopener noreferrer">Open in new tab: { to }</a>
      </iframe>
    </div>
  );
}
