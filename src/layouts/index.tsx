import * as React from "react"
import Sidebar from "../components/Sidebar"

interface Props {
  children: React.ReactNode
}

const Layout = ({ children }: Props) => {
  return (
    <div className="dark:bg-[#111111] min-h-screen">
      <div className="max-w-[1400px] mx-auto md:px-4 lg:px-8">
        <div
          className="h-0 overflow-y-auto transition-all duration-400 bg-white dark:bg-black z-30 \
            fixed h-[4rem] focus:h-screen focus-within:h-screen active:h-screen w-full \
            md:h-screen md:w-[220px] \
            lg:w-[260px] \
            xl:w-[280px] \
        ">
          <Sidebar></Sidebar>
        </div>
        <div className="px-8 pt-[5rem] md:pr-0 md:pl-[250px] md:pt-0 lg:pl-[290px] xl:pl-[330px]">
          { children }
        </div>
      </div>
    </div>
  )
}

export default Layout
