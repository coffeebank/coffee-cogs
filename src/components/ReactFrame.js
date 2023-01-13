import React from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';

export default function ReactFrame(props) {
  return (
    <div
      css={css`
        height: ${props.height}px;
        width: 100%;
        border-radius: 5px;
        overflow: hidden;
      `}
    >
      <iframe
        src={props.to}
        css={css`
            height: ${props.height}px;
            width: 100%;
            border: 0;
          `}
        title={props.title || props.to}
      >
        <a href={props.to} target={props.newTab === true ? '_blank' : ''} rel="noopener noreferrer">Open in new tab: { props.to }</a>
      </iframe>
    </div>
  );
}

ReactFrame.propTypes = {
  to: PropTypes.string,
  height: PropTypes.number,
  newTab: PropTypes.bool
};

ReactFrame.defaultProps = {
  height: 400,
  newTab: true
};
