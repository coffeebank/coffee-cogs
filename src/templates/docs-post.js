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
    <section className="w-full flex flex-wrap gap-x-[45px] lg:flex-nowrap pt-nav justify-start">
      <main
        className="w-full max-w-[710px] text-[#2c3e50] dark:text-[#faf9f7] \
          prose prose-neutral dark:prose-invert \
          prose-a:transition-colors \
          prose-h1:font-bold prose-h1:text-[2rem] prose-h1:mb-[20px] prose-h1:text-black/80 dark:prose-h1:text-white \
          prose-h2:text-[1.65rem] prose-h2:pb-[0.3rem] prose-h2:text-black/90 dark:prose-h2:text-white \
          prose-h2:border-b-[1px] prose-h2:border-[#eaecef] dark:prose-h2:border-[#515355] \
          prose-img:rounded-lg prose-img:mt-0 prose-img:mb-[1.25em] \
          prose-pre:bg-black/5 dark:prose-pre:bg-white/[0.075] \
          prose-pre:text-gray-600 dark:prose-pre:text-gray-200 \
          prose-pre:rounded-md \
          [&_blockquote_p:first-of-type::before]:content-none [&_blockquote_p:first-of-type::after]:content-none \
          dark:[&_a.anchor]:fill-purple-500 \
          [&_.anchor.before]:h-full [&_.anchor.before]:flex [&_.anchor.before]:items-center \
        "
      >
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
      </main>
      <aside className="w-full lg:max-w-[235px] h-full sticky top-0">
        <div className="pt-20">
          <h2 className="font-bold text-sm uppercase text-black/80 dark:text-white/80">On this page</h2>
          <div
            className="py-2 text-sm [&_li>p]:hidden [&_li]:py-1 hover:[&_li>a]:text-purple-700 [&_li]:transition-all"
            dangerouslySetInnerHTML={{ __html: post.tableOfContents }}
          />
        </div>
      </aside>
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
