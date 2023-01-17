import * as React from "react"
import { Link, graphql } from "gatsby"
import rehypeReact from "rehype-react"

import Seo from "../components/seo"
import CogFork from "../components/CogFork"
import CogHero from "../components/CogHero"
import ReactButton from "../components/ReactButton"
import ReactFrame from "../components/ReactFrame"

const renderAst = new rehypeReact({
  createElement: React.createElement,
  components: {
    "component-cogfork": CogFork,
    "component-coghero": CogHero,
    "component-reactbutton": ReactButton,
    "component-reactframe": ReactFrame,
  },
}).Compiler

const BlogPostTemplate = ({
  data: { previous, next, site, markdownRemark: post },
}) => {
  return (
    <section>
      {/* <div
        dangerouslySetInnerHTML={{ __html: post.html }}
        itemProp="articleBody"
      /> */}
      {renderAst(post.htmlAst)}
      <hr />
      <nav className="blog-post-nav">
        <ul
          style={{
            display: `flex`,
            flexWrap: `wrap`,
            justifyContent: `space-between`,
            listStyle: `none`,
            padding: 0,
          }}
        >
          <li>
            {previous && (
              <Link to={previous.fields.slug} rel="prev">
                ← {previous.frontmatter.title}
              </Link>
            )}
          </li>
          <li>
            {next && (
              <Link to={next.fields.slug} rel="next">
                {next.frontmatter.title} →
              </Link>
            )}
          </li>
        </ul>
      </nav>
    </section>
  )
}

export const Head = ({ data: { markdownRemark: post } }) => {
  return (
    <Seo
      title={post.frontmatter.title}
      description={post.frontmatter.description || post.excerpt}
    />
  )
}

export default BlogPostTemplate

export const pageQuery = graphql`
  query BlogPostBySlug(
    $id: String!
    $previousPostId: String
    $nextPostId: String
  ) {
    site {
      siteMetadata {
        title
      }
    }
    markdownRemark(id: { eq: $id }) {
      id
      excerpt(pruneLength: 160)
      html
      htmlAst
      tableOfContents
      frontmatter {
        title
        date(formatString: "MMMM DD, YYYY")
        description
      }
    }
    previous: markdownRemark(id: { eq: $previousPostId }) {
      fields {
        slug
      }
      frontmatter {
        title
      }
    }
    next: markdownRemark(id: { eq: $nextPostId }) {
      fields {
        slug
      }
      frontmatter {
        title
      }
    }
  }
`
