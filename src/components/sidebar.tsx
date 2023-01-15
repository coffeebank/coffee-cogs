import React from 'react';
import { Link } from "gatsby"

export default function Sidebar() {
  const sidebarItems = [
    {
      title: "Title 1",
      heading: false,
      items: [
        {
          title: "Hello World!",
          link: "/hello-world"
        },
        {
          title: "My Second Post",
          link: "/my-second-post"
        }
      ]
    },
    {
      title: "Title 2",
      heading: true,
      items: [
        {
          title: "New Beginnings",
          link: "/new-beginnings"
        }
      ]
    }
  ]
  
  const currentYear = new Date().getFullYear();

  return (
    <div>
      <div>
        <Link to="/" aria-label="Go to home page">
          <h1>Title</h1>
        </Link>
      </div>
      <nav>
        {sidebarItems.map(({ title, heading, items }) => {
          const subitems = items.map((item, index) => (
            <li key={item.title+index}><Link to={item.link}>{item.title}</Link></li>
          ));

          return (
            <>
              { heading === true ? (
                <h2>{ title }</h2>
              ) : '' }
              <ul key={title+heading}>
                { subitems }
              </ul>
            </>
          );
        })}
      </nav>
      <div style={{width:'100%',padding:'2em',fontSize:'0.9em',color:'rgba(0,0,0,0.6)'}}>
        &copy; {currentYear} Coffeebank ☕🏦 <br />
        <a href="https://coffeebank.github.io/" target="_blank" rel="noopener" style={{color:'rgba(0,0,0,0.6)'}}>Home</a>&ensp;
        <a href="https://github.com/coffeebank/coffee-cogs/" target="_blank" rel="noopener" style={{color:'rgba(0,0,0,0.6)'}}>GitHub</a>&ensp;
        <a href="https://github.com/coffeebank/coffee-cogs/blob/master/LICENSE" target="_blank" rel="noopener" style={{color:'rgba(0,0,0,0.6)'}}>License</a>
      </div>
    </div>
  );
}
