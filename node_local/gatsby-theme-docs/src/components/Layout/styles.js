import styled from '@emotion/styled';

export const Container = styled.div`
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;

  display: grid;
  grid-template-columns: 280px calc(100% - 320px);
  grid-auto-flow: row;
  grid-gap: 40px;

  @media (max-width: 780px) {
    padding: 6rem 32px 32px;
    grid-template-columns: 100%;
  }

  /* jost-300 - latin */
  @font-face {
    font-family: 'Jost';
    font-style: normal;
    font-weight: 300;
    src: local(''),
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-300.woff2') format('woff2'), /* Chrome 26+, Opera 23+, Firefox 39+ */
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-300.woff') format('woff'); /* Chrome 6+, Firefox 3.6+, IE 9+, Safari 5.1+ */
  }

  /* jost-regular - latin */
  @font-face {
    font-family: 'Jost';
    font-style: normal;
    font-weight: 400;
    src: local(''),
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-regular.woff2') format('woff2'), /* Chrome 26+, Opera 23+, Firefox 39+ */
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-regular.woff') format('woff'); /* Chrome 6+, Firefox 3.6+, IE 9+, Safari 5.1+ */
  }

  /* jost-500 - latin */
  @font-face {
    font-family: 'Jost';
    font-style: normal;
    font-weight: 500;
    src: local(''),
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-500.woff2') format('woff2'), /* Chrome 26+, Opera 23+, Firefox 39+ */
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-500.woff') format('woff'); /* Chrome 6+, Firefox 3.6+, IE 9+, Safari 5.1+ */
  }

  /* jost-600 - latin */
  @font-face {
    font-family: 'Jost';
    font-style: normal;
    font-weight: 600;
    src: local(''),
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-600.woff2') format('woff2'), /* Chrome 26+, Opera 23+, Firefox 39+ */
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-600.woff') format('woff'); /* Chrome 6+, Firefox 3.6+, IE 9+, Safari 5.1+ */
  }

  /* jost-700 - latin */
  @font-face {
    font-family: 'Jost';
    font-style: normal;
    font-weight: 700;
    src: local(''),
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-700.woff2') format('woff2'), /* Chrome 26+, Opera 23+, Firefox 39+ */
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-700.woff') format('woff'); /* Chrome 6+, Firefox 3.6+, IE 9+, Safari 5.1+ */
  }

  /* jost-800 - latin */
  @font-face {
    font-family: 'Jost';
    font-style: normal;
    font-weight: 800;
    src: local(''),
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-800.woff2') format('woff2'), /* Chrome 26+, Opera 23+, Firefox 39+ */
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-800.woff') format('woff'); /* Chrome 6+, Firefox 3.6+, IE 9+, Safari 5.1+ */
  }

  /* jost-300italic - latin */
  @font-face {
    font-family: 'Jost';
    font-style: italic;
    font-weight: 300;
    src: local(''),
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-300italic.woff2') format('woff2'), /* Chrome 26+, Opera 23+, Firefox 39+ */
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-300italic.woff') format('woff'); /* Chrome 6+, Firefox 3.6+, IE 9+, Safari 5.1+ */
  }

  /* jost-italic - latin */
  @font-face {
    font-family: 'Jost';
    font-style: italic;
    font-weight: 400;
    src: local(''),
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-italic.woff2') format('woff2'), /* Chrome 26+, Opera 23+, Firefox 39+ */
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-italic.woff') format('woff'); /* Chrome 6+, Firefox 3.6+, IE 9+, Safari 5.1+ */
  }

  /* jost-500italic - latin */
  @font-face {
    font-family: 'Jost';
    font-style: italic;
    font-weight: 500;
    src: local(''),
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-500italic.woff2') format('woff2'), /* Chrome 26+, Opera 23+, Firefox 39+ */
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-500italic.woff') format('woff'); /* Chrome 6+, Firefox 3.6+, IE 9+, Safari 5.1+ */
  }

  /* jost-600italic - latin */
  @font-face {
    font-family: 'Jost';
    font-style: italic;
    font-weight: 600;
    src: local(''),
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-600italic.woff2') format('woff2'), /* Chrome 26+, Opera 23+, Firefox 39+ */
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-600italic.woff') format('woff'); /* Chrome 6+, Firefox 3.6+, IE 9+, Safari 5.1+ */
  }

  /* jost-700italic - latin */
  @font-face {
    font-family: 'Jost';
    font-style: italic;
    font-weight: 700;
    src: local(''),
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-700italic.woff2') format('woff2'), /* Chrome 26+, Opera 23+, Firefox 39+ */
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-700italic.woff') format('woff'); /* Chrome 6+, Firefox 3.6+, IE 9+, Safari 5.1+ */
  }

  /* jost-800italic - latin */
  @font-face {
    font-family: 'Jost';
    font-style: italic;
    font-weight: 800;
    src: local(''),
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-800italic.woff2') format('woff2'), /* Chrome 26+, Opera 23+, Firefox 39+ */
        url('https://coffeebank.github.io/home/fonts/jost/jost-v14-latin-800italic.woff') format('woff'); /* Chrome 6+, Firefox 3.6+, IE 9+, Safari 5.1+ */
  }
`;

export const Main = styled.main`
  height: 100%;
  padding-top: 36px;
  width: 100%;

  display: flex;
  justify-content: flex-start;
  position: relative;

  @media (max-width: 1200px) {
    flex-direction: column;
  }

  @media (max-width: 780px) {
    padding-top: 0;
  }
`;

export const Children = styled.div`
  width: 100%;
  max-width: calc(75% - 64px);
  padding-right: 64px;

  @media (max-width: 1200px) {
    max-width: 100%;
    padding-right: 0;
  }

  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    overflow-wrap: break-word;
  }
`;
