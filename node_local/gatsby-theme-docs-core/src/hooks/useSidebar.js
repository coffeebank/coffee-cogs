import { graphql, useStaticQuery } from 'gatsby';
import { resolveLink } from '../../util/url';

export function useSidebar() {
  const data = useStaticQuery(graphql`
    {
      allSidebarItems {
        edges {
          node {
            label
            link
            items {
              label
              link
            }
            id
          }
        }
      }
    }
  `);

  const {
    allSidebarItems: { edges },
  } = data;

  return edges;
}
