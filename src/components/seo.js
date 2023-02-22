/**
 * SEO component that queries for data with
 * Gatsby's useStaticQuery React hook
 *
 * See: https://www.gatsbyjs.com/docs/how-to/querying-data/use-static-query/
 */

import * as React from "react"
import { useStaticQuery, graphql } from "gatsby"

const Seo = ({ description, title, children }) => {
  const { site } = useStaticQuery(
    graphql`
      query {
        site {
          siteMetadata {
            title
            description
            social {
              twitter
            }
          }
        }
      }
    `
  )

  const metaDescription = description || site.siteMetadata.description
  const defaultTitle = site.siteMetadata?.title

  return (
    <>
      <title>{ title ? (defaultTitle ? `${title} | ${defaultTitle}` : title) : "Coffee Cogs ☕" }</title>
      <meta name="description" content={ metaDescription ? metaDescription : "Documentation site for Coffee Cogs ☕" } />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={ metaDescription ? metaDescription : "Documentation site for Coffee Cogs ☕" } />
      <meta property="og:image" content="/coffee-cogs-rd.png" />
      <meta property="og:image:type" content="image/png" />
      <meta property="og:image:width" content="200" />
      <meta property="og:image:height" content="200" />
      <meta name="twitter:card" content="summary" />
      <meta
        name="twitter:creator"
        content={site.siteMetadata?.social?.twitter || ``}
      />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={metaDescription} />
      {children}
    </>
  )
}

export default Seo
