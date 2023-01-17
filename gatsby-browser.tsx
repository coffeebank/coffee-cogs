import React from "react"
import Layout from "./src/layouts"

// custom typefaces
// normalize CSS across browsers
// custom CSS styles
import "./src/style.css"

// Highlighting for code blocks
// import "prismjs/themes/prism.css"

export function wrapPageElement({ element, props }) {
  return <Layout {...props}>{element}</Layout>
}
