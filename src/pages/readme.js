import * as React from "react"
import { graphql } from "gatsby"

import Layout from "../layouts"
import Seo from "../components/seo"

const ReadmePage = ({ data, location }) => {
  const siteTitle = data.site.siteMetadata.title
  fetch('https://raw.githubusercontent.com/Cog-Creators/Red-Index/master/index/1-min.json')
  .then(resp => resp.json())
  .then(data => {
    let coffeecogs = data["https://github.com/coffeebank/coffee-cogs"].rx_cogs;
    let repoDetails = document.getElementById("repoDetails");
    Object.keys(coffeecogs).forEach(function(cog){
      repoDetails.innerHTML += `|[${cog}](https://coffeebank.github.io/coffee-cogs/${cog})|${coffeecogs[cog].description.replace("|", "\\|")}|<br>`;
    });
  });

  return (
    <div className="p-8">
      <div id="repoDetails"></div>
    </div>
  )
}

export const Head = () => <Seo title="README.md" />

export default ReadmePage

export const pageQuery = graphql`
  query {
    site {
      siteMetadata {
        title
      }
    }
  }
`
