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
          { children }
        </div>
      </div>
    </div>
  )
}

export default Layout
