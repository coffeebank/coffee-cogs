import * as React from "react"
import Sidebar from "../components/Sidebar"

interface Props {
  children: React.ReactNode
}

const Layout = ({ children }: Props) => {
  return (
    <div className="dark:bg-[#111111] min-h-screen">
      <div className="max-w-[1400px] mx-auto sm:px-8">
        <div className="fixed w-[260px] xl:w-[280px] h-screen overflow-y-auto">
          <Sidebar></Sidebar>
        </div>
        <div className="pl-[310px] lg:pl-[330px]">
          <section className="w-full flex flex-wrap gap-x-[45px] lg:flex-nowrap pt-nav justify-start">
            <main
              className="w-full max-w-[710px] text-[#2c3e50] dark:text-[#faf9f7] \
                prose prose-neutral dark:prose-invert \
                prose-a:transition-colors \
                prose-h1:font-bold prose-h1:text-[2rem] prose-h1:mb-[20px] prose-h1:text-black/80 dark:prose-h1:text-white \
                prose-h2:text-[1.65rem] prose-h2:pb-[0.3rem] prose-h2:border-b-[1px] dark:prose-h2:text-white prose-h2:border-[#eaecef] dark:prose-h2:border-[#515355] \
                prose-img:rounded-lg prose-img:mt-0 prose-img:mb-[1.25em] \
                prose-pre:bg-black/5 dark:prose-pre:bg-white/[0.075] \
                prose-pre:text-gray-600 dark:prose-pre:text-gray-200 \
                prose-pre:rounded-md \
                [&_blockquote_p:first-of-type::before]:content-none [&_blockquote_p:first-of-type::after]:content-none \
                dark:[&_a.anchor]:fill-purple-500 \
                [&_.anchor.before]:h-full [&_.anchor.before]:flex [&_.anchor.before]:items-center \
              "
            >
              { children }
            </main>
            <aside className="w-full lg:max-w-[235px] h-full sticky top-0">
              <div className="pt-20">
                <h2 className="font-bold text-sm uppercase text-black/80 dark:text-white/80">On this page</h2>
              </div>
            </aside>
          </section>
        </div>
      </div>
    </div>
  )
}

export default Layout
