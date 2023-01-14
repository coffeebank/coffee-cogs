module.exports = {
  siteMetadata: {
    siteTitle: `Coffee Cogs ☕`,
    defaultTitle: `Coffee Cogs ☕`,
    siteTitleShort: `Coffee Cogs ☕`,
    siteDescription: `coffee-cogs`,
    siteUrl: `https://coffeebank.github.io`,
    siteAuthor: `@coffeebank`,
    siteImage: `/banner.png`,
    siteLanguage: `en`,
    themeColor: `#8257E6`,
    basePath: `/coffee-cogs`,
  },
  pathPrefix: '/coffee-cogs',
	trailingSlash: 'always',
  plugins: [
    {
      resolve: `@rocketseat/gatsby-theme-docs`,
      options: {
        configPath: `src/config`,
        docsPath: `src/docs`,
        yamlFilesPath: `src/yamlFiles`,
        repositoryUrl: `https://github.com/coffeebank/coffee-cogs`,
        branch: `docs/src`,
        baseDir: ``,
        gatsbyRemarkPlugins: [],
      },
    },
    {
      resolve: `gatsby-plugin-manifest`,
      options: {
        name: `Rocket Docs`,
        short_name: `Rocket Docs`,
        start_url: `/coffee-cogs/`,
        background_color: `#ffffff`,
        display: `standalone`,
        icon: `static/favicon.png`,
      },
    },
    `gatsby-plugin-postcss`,
    `gatsby-plugin-sitemap`,
    {
      resolve: `gatsby-plugin-canonical-urls`,
      options: {
        siteUrl: `https://coffeebank.github.io/coffee-cogs`,
      },
    },
    `gatsby-plugin-offline`,
  ],
};
