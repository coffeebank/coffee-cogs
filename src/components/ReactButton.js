import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'gatsby';

export default function ReactButton(props) {
  return (
    <div className={'mb-[24px] '+props.className}>
      <Link to={props.to} target={props.newTab === true ? '_blank' : ''} rel="noopener noreferrer" className="!no-underline inline-block">
        { props.children ? (
          props.children
        ) : (
          <div className={ "px-6 py-3 transition duration-300 rounded-md !no-underline "+props.classButton }>
            { props.body }
          </div>
        )}
      </Link>
    </div>
  );
}

ReactButton.propTypes = {
  to: PropTypes.string,
  className: PropTypes.string,
  classButton: PropTypes.string,
  body: PropTypes.string,
  newTab: PropTypes.bool
};

ReactButton.defaultProps = {
  className: "",
  classButton: "bg-purple-800 hover:bg-purple-700 text-white",
  body: "Open Link",
  newTab: true
};
