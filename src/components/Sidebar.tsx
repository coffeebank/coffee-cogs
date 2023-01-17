import React from 'react';
import { Link } from "gatsby"

export default function Sidebar() {
  const sidebarItems = [
    {
      title: "Title 1",
      heading: false,
      items: [
        {
          title: "Home",
          link: "/"
        },
        {
          title: "Getting Started",
          link: "/start"
        }
      ]
    },
    {
      title: "🍒 Cherry Emotes",
      heading: true,
      items: [
        {
          title: "Home",
          link: "/emotes"
        }
      ]
    },
    {
      title: "🐱 Hellohook",
      heading: true,
      items: [
        {
          title: "Home",
          link: "/hellohook"
        }
      ]
    },
    {
      title: "📮 Msgmover",
      heading: true,
      items: [
        {
          title: "Home",
          link: "/msgmover"
        }
      ]
    },
    {
      title: "More cogs",
      heading: true,
      items: [
        {
          title: "bartender",
          link: "/bartender"
        },
        {
          title: "coffeetime",
          link: "/coffeetime"
        },
        {
          title: "coffeetools",
          link: "/coffeetools"
        },
        {
          title: "dmreply",
          link: "/dmreply"
        },
        {
          title: "jsonrequest",
          link: "/jsonrequest"
        },
        {
          title: "kyarutail",
          link: "/kyarutail"
        },
        {
          title: "loveplay",
          link: "/loveplay"
        },
        {
          title: "pinboard",
          link: "/pinboard"
        },
        {
          title: "quarantine",
          link: "/quarantine"
        },
        {
          title: "sendhook",
          link: "/sendhook"
        },
        {
          title: "spotifyembed",
          link: "/spotifyembed"
        },
        {
          title: "websearch",
          link: "/websearch"
        },
      ]
    }
  ]
  
  const currentYear = new Date().getFullYear();

  return (
    <aside className="w-full min-h-screen pt-nav flex flex-col justify-between px-2 gap-6">
      <header>
        <Link to="/" aria-label="Go to home page">
          <div className="w-full px-4 pt-1 pb-4 min-h-[4rem]">
            <h1 className="font-bold text-xl text-black/90 dark:text-white/90">Coffee Cogs ☕</h1>
          </div>
        </Link>
        <nav className="pt-4">
          {sidebarItems.map(({ title, heading, items }) => {
            const subitems = items.map((item, index) => (
              <li key={ item.title + '-' + item.link + '-' + index }>
                <Link to={ item.link } activeClassName="active" partiallyActive={false} className="[&.active>div]:bg-purple-700/90 dark:[&.active>div]:bg-purple-800/90 [&.active>div]:text-white transition-all duration-200">
                  <div className="py-[0.5rem] px-3 truncate text-[0.95rem] text-black/90 dark:text-white/80 rounded">{ item.title }</div>
                </Link>
              </li>
            ));

            return (
              <>
                { heading === true ? (
                  <h2 className="px-2 pt-7 pb-2 font-bold dark:font-thick text-black/90 dark:text-white/90">{ title }</h2>
                ) : '' }
                <ul key={ title + heading } className="px-2">
                  { subitems }
                </ul>
              </>
            );
          })}
        </nav>
      </header>
      <footer className="w-full px-5 py-8 text-[0.9rem] text-black/60 dark:text-white/70 [&>_a]:font-bold hover:[&>_a]:underline [&>_a]:text-black/60 dark:[&>_a]:text-white/70">
        &copy; {currentYear} Coffeebank ☕🏦 <br />
        <a href="https://coffeebank.github.io/" target="_blank" rel="noopener">Home</a>&ensp;
        <a href="https://github.com/coffeebank/coffee-cogs/" target="_blank" rel="noopener">GitHub</a>&ensp;
        <a href="https://github.com/coffeebank/coffee-cogs/blob/master/LICENSE" target="_blank" rel="noopener">License</a>
      </footer>
    </aside>
  );
}
