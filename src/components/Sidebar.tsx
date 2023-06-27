import React from 'react';
import { Link } from "gatsby"
import Footer from './Footer';

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
      title: "📚 Dictionaries",
      heading: true,
      items: [
        {
          title: "Chinese 字典",
          link: "/zidian"
        },
        {
          title: "Japanese 辞書",
          link: "/jadict"
        },
        {
          title: "Korean 사전",
          link: "/kodict"
        },
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
          title: "coffeeani",
          link: "/coffeeani"
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
          title: "emotes",
          link: "/emotes"
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
    },
    {
      title: "About",
      heading: true,
      items: [
        {
          title: "Red 3.4",
          link: "/red-34/"
        },
      ]
    },
  ]

  return (
    <aside className="w-full min-h-screen md:pt-nav flex flex-col justify-between px-2 gap-6">
      <header>
        <div className="w-full px-4 md:pt-1 md:pb-4 min-h-[4rem] flex items-center align-middle justify-between md:block">
          <Link to="/" aria-label="Go to home page">
            <h1 className="font-bold text-xl text-black/90 dark:text-white/90">Coffee Cogs ☕</h1>
          </Link>
          <div className="md:hidden">
            <button className="dark:text-gray-200">
              Menu
            </button>
          </div>
        </div>
        <nav className="pt-4 px-8 md:px-0">
          {sidebarItems.map(({ title, heading, items }) => {
            let keyNum = Math.floor(Math.random() * (99 - 11) + 11);

            const subitems = items.map((item, index) => (
              <li key={ item.toString() + index + keyNum }>
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
                <ul className="px-2">
                  { subitems }
                </ul>
              </>
            );
          })}
        </nav>
      </header>
      <footer className="w-full px-5 py-8 text-[0.9rem] text-black/60 dark:text-white/70 [&>_a]:font-bold hover:[&>_a]:underline [&>_a]:text-black/60 dark:[&>_a]:text-white/70">
        <Footer />
      </footer>
    </aside>
  );
}
