import React from 'react';
import PropTypes from 'prop-types';
import styled from '@emotion/styled';
import { GiHamburgerMenu } from 'react-icons/gi';
import { useStaticQuery, graphql } from 'gatsby';

const Container = styled.header`
  position: fixed;
  width: 100%;
  padding: 1.25rem 32px;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(30px);
  z-index: 2001;
  top: 0;
  left: 0;

  display: flex;
  justify-content: flex-start;
  align-items: center;

  h2 {
    margin: 0;
    border: none;
    padding: 0;
    font-size: 18px;

    @media (max-width: 359px) {
      font-size: 14px;
    }
  }

  button {
    border: none;
    background: none;
    cursor: pointer;
    margin-right: 16px;

    display: flex;
    justify-content: flex-start;
    align-items: center;
  }

  @media (min-width: 780px) {
    display: none;
  }
`;

export default function Header({ handleMenuOpen }) {
  const { site } = useStaticQuery(
    graphql`
      query {
        site {
          siteMetadata {
            siteTitle
          }
        }
      }
    `,
  );

  const { siteTitle } = site.siteMetadata;

  return (
    <Container>
      <button aria-label="Open sidebar" type="button" onClick={handleMenuOpen}>
        <GiHamburgerMenu size={23} aria-hidden="true" />
      </button>
      <h2>{siteTitle}</h2>
    </Container>
  );
}

Header.propTypes = {
  handleMenuOpen: PropTypes.func.isRequired,
};
