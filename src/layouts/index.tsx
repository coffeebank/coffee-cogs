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
        <div className="pl-[300px] lg:pl-[320px]">
          <section className="w-full flex flex-wrap gap-x-[45px] lg:flex-nowrap pt-nav justify-start">
            <main
              className="w-full max-w-[710px] \
                prose prose-neutral dark:prose-invert \
                prose-a:transition-colors \
                dark:text-[#e6e4e2]
                prose-img:rounded-lg \
                prose-pre:bg-black/5 dark:prose-pre:bg-white/[0.075] \
                prose-pre:text-gray-600 dark:prose-pre:text-gray-200 \
                prose-pre:rounded-md \
                [&_.anchor.before]:h-full \
                [&_.anchor.before]:flex [&_.anchor.before]:items-center \
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
