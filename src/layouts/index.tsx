import * as React from "react"
import { useEffect } from "react"
import { useLocation } from "@reach/router"
import Sidebar from "../components/Sidebar"

interface Props {
  children: React.ReactNode
}

const Layout = ({ children }: Props) => {
  const location = useLocation()

  useEffect(() => {
    // Client only
    try { process } catch (e) {
      if (JSON.parse(localStorage.getItem("catsIgnore")) !== "true" && window.location.hostname !== "localhost") {
        console.log('🐱 loaded '+location.pathname);
        
        // collect variables
        let catsSession;
        let catsTime;
        let dateObj;
        let catsUserAgent;
        let catsPage;
  
        try {
          // use iso timestamp as session id
          if (localStorage.getItem("catsSession")) {
            // ongoing session
            catsSession = localStorage.getItem("catsSession");
            dateObj = new Date();
            catsTime = dateObj.toString();
          } else {
            // new session
            dateObj = new Date();
            catsSession = Date.parse(dateObj);
            catsTime = dateObj.toString();
            localStorage.setItem("catsSession", catsSession);
          }
          console.log("catsjs: session timestamp " + catsSession);
  
          catsUserAgent = navigator.userAgent;
          catsPage = location.pathname;
        } catch (error) {
          console.log({ error }, "catsjs: variable collect error");
        }

        // send to database
        try {
          const catsPostOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json", },
            body: JSON.stringify({
              sessionId: catsSession,
              time: catsTime,
              useragent: catsUserAgent,
              page: catsPage,
            })
          };
          fetch("https://coffeebank.netlify.app/.netlify/functions/postCats", catsPostOptions)
            .then(catsPostResp => console.log("catsjs: updated " + catsPage))
            .catch((error) => {
              console.log(error)
            });
        } catch (error) {
          console.log({ error }, "catsjs: couldn't connect")
        }
      } else {
        console.log("catsjs: excluded device");
      }
    }
  }, [location.pathname])

  return (
    <div className="dark:bg-[#111111] min-h-screen">
      <div className="max-w-[1400px] mx-auto md:pl-2 md:pr-6 lg:px-8">
        <div
          className="h-0 overflow-y-auto transition-all duration-400 bg-white dark:bg-[#111111] z-30 \
            fixed h-[4rem] focus:h-screen focus-within:h-screen active:h-screen w-full \
            md:h-screen md:w-[220px] \
            lg:w-[260px] lg:px-0 \
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
