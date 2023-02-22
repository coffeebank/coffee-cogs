import React from 'react';
import { Link } from 'gatsby';
import useFetch from '../hooks/useFetch';

interface Props extends React.ProfilerProps {
  cog: string,
  desc: string,
}

interface CogData {
  name?: string,
  description?: string,
  end_user_data_statement?: string,
  tags?: string[],
}

const CogHero = (props: Props) => {
  const cogData: CogData = (
    useFetch("https://github.com/coffeebank/coffee-cogs/blob/master/" + props.cog + "/info.json?raw=true")
  ) || {} ;

  return (
    <div>
      <div className="transition-opacity duration-150">
        <div className="text-xl whitespace-pre-line">{ cogData.description || props.desc || (
          <div className="w-full h-16 rounded-lg bg-black/5 dark:bg-white/30 animate-pulse"></div>
        ) }</div>
        {cogData.tags ? (
          <div className="pt-4 flex flex-wrap">
            {cogData.tags.map((ct: string) =>
              <div key={ct} className="mx-1 mt-1 px-2 py-1 bg-gray-300 text-gray-800 rounded text-xs select-none">{ ct }</div>
            )}
          </div>
        ) : (
          <div className="pt-4 flex flex-wrap">
            <div className="mx-1 mt-1 px-2 py-1 animate-pulse bg-gray-300 dark:bg-white/30 text-gray-800 rounded text-xs select-none">...</div>
            <div className="mx-1 mt-1 px-2 py-1 animate-pulse bg-gray-300 dark:bg-white/30 text-gray-800 rounded text-xs select-none">...</div>
            <div className="mx-1 mt-1 px-2 py-1 animate-pulse bg-gray-300 dark:bg-white/30 text-gray-800 rounded text-xs select-none">...</div>
          </div>
        )}
        <div className="pt-10 font-bold">Install</div>
        <div className="py-2 text-sm">New here? <Link to="/start/">See the Getting Started guide&ensp;▸</Link></div>
        <div className="px-5 py-4 sm:py-3 rounded-md bg-black/5 dark:bg-white/[0.075]" title="Replace [p] with your bot's prefix">
          <pre className="m-0 p-0 !bg-transparent text-gray-600 text-sm overflow-x-auto leading-6">
            <span className="select-none">[p]</span><span className="select-all sm:select-auto">repo add coffee-cogs https://github.com/coffeebank/coffee-cogs</span><br />
            <span className="select-none">[p]</span><span className="select-all sm:select-auto">cog install coffee-cogs { cogData.name || props.cog }</span>
          </pre>
        </div>
        <div className="pt-2 text-sm">{ cogData.end_user_data_statement || "" }</div>
      </div>
      <div className="pt-2 pb-10 text-sm"><a href={'https://github.com/coffeebank/coffee-cogs/tree/master/'+props.cog} rel="noopener" target="_blank">Browse Source Code</a></div>
    </div>
  );
}

export default CogHero;
