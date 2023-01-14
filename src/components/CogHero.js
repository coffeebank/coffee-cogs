import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'gatsby';

class CogHero extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: true,
      error: false,
      cogData: {}
    };
  }

  componentDidMount() {
    let cogUrl = "https://raw.githubusercontent.com/coffeebank/coffee-cogs/master/"+this.props.cog+"/info.json";
    fetch(cogUrl)
      .then(resp => {
        return resp.json();
      })
      .then(json => {
        this.setState({
          cogData: json,
          loading: false
        });
        return this.state;
      })
      .catch(err => {
        console.log(err);
      })
  }

  render() {
    const { loading, cogData } = this.state
    
    return (
      <div>
        <div className="transition-opacity duration-150">
          <div className="text-xl whitespace-pre-line">{ cogData.description || this.props.desc || "⏳" }</div>
          {cogData.tags ? (
            <div className="pt-4 flex flex-wrap">
              {cogData.tags.map(ct =>
                <div key={ct} className="mx-1 mt-1 px-2 py-1 bg-gray-300 text-gray-800 rounded text-xs select-none">{ ct }</div>
              )}
            </div>
          ):''}
          <div className="pt-10 font-bold">Install</div>
          <div className="py-2 text-sm">New here? <Link to="/coffee/start/">See the Getting Started guide&ensp;▸</Link></div>
          <div className="px-5 py-4 sm:py-3 rounded-md bg-black/5" title="Replace [p] with your bot's prefix">
            <pre className="text-gray-600 text-sm overflow-x-auto leading-6">
              <span className="select-none">[p]</span><span className="select-all sm:select-auto">repo add coffee-cogs https://github.com/coffeebank/coffee-cogs</span><br />
              <span className="select-none">[p]</span><span className="select-all sm:select-auto">cog install coffee-cogs { cogData.name || this.props.cog }</span>
            </pre>
          </div>
          <div className="pt-2 text-sm">{ cogData.end_user_data_statement || "" }</div>
        </div>
        <div className="pt-2 pb-10 text-sm"><a href={'https://github.com/coffeebank/coffee-cogs/tree/master/'+this.props.cog} rel="noopener" target="_blank">Browse Source Code</a></div>
      </div>
    );
  }
}

export default CogHero;

CogHero.propTypes = {
  cog: PropTypes.string,
  desc: PropTypes.string
};

CogHero.defaultProps = {
  cog: 'hellohook',
  desc: '⏳'
};
