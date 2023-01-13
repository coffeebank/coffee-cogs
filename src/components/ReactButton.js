import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'gatsby';

export default function ReactButton(props) {
  return (
    <div className={'mb-[24px] '+props.className}>
      <Link to={props.to} target={props.newTab === true ? '_blank' : ''} rel="noopener noreferrer" className="!no-underline inline-block">
        <div className="px-6 py-3 bg-purple-800 hover:bg-purple-700 text-white transition duration-300 rounded-md !no-underline">
          { props.body }
        </div>
      </Link>
    </div>
  );
}

ReactButton.propTypes = {
  to: PropTypes.string,
  className: PropTypes.string,
  body: PropTypes.string,
  newTab: PropTypes.bool
};

ReactButton.defaultProps = {
  className: "",
  body: "Open Link",
  newTab: true
};
