const withDefault = require('@rocketseat/gatsby-theme-docs-core/util/with-default');

module.exports = (options) => {
  const themeOptions = withDefault(options);

  return {
    siteMetadata: {
      siteLanguage: `en`,
      basePath: themeOptions.basePath,
      docsPath: themeOptions.docsPath,
    },
    plugins: [
      {
        resolve: `@rocketseat/gatsby-theme-docs-core`,
        options: themeOptions,
      },
      `gatsby-plugin-catch-links`,
      `gatsby-plugin-emotion`,
      `gatsby-plugin-react-helmet`,
    ].filter(Boolean),
  };
};
