module.exports = {
  pathPrefix: '/coffee-cogs/',
  siteMetadata: {
    siteTitle: `Coffee Cogs ☕`,
    defaultTitle: `Coffee Cogs ☕`,
    siteTitleShort: `Coffee Cogs ☕`,
    siteDescription: `coffee-cogs`,
    siteUrl: `https://coffeebank.github.io/coffee-cogs`,
    siteAuthor: `@coffeebank`,
    siteImage: `/banner.png`,
    siteLanguage: `en`,
    themeColor: `#8257E6`,
    basePath: `/`,
  },
  plugins: [
    {
      resolve: `@rocketseat/gatsby-theme-docs`,
      options: {
        configPath: `src/config`,
        docsPath: `src/docs`,
        yamlFilesPath: `src/yamlFiles`,
        repositoryUrl: `https://github.com/coffeebank/coffee-cogs`,
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
    `gatsby-plugin-sitemap`,
    // {
    //   resolve: `gatsby-plugin-google-analytics`,
    //   options: {
    //     trackingId: `YOUR_ANALYTICS_ID`,
    //   },
    // },
    `gatsby-plugin-remove-trailing-slashes`,
    {
      resolve: `gatsby-plugin-canonical-urls`,
      options: {
        siteUrl: `https://coffeebank.github.io/coffee-cogs`,
      },
    },
    `gatsby-plugin-offline`,
  ],
};
