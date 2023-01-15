/* eslint-disable */
import React from 'react';
import { preToCodeBlock } from 'mdx-utils';
import { MDXProvider } from '@mdx-js/react';

import Code from '../src/components/Code';
import CogFork from '../../../src/components/CogFork';
import CogHero from '../../../src/components/CogHero';
import ReactButton from '../../../src/components/ReactButton';
import ReactFrame from '../../../src/components/ReactFrame';

const shortcodes = { CogFork, CogHero, ReactButton, ReactFrame }

const components = {
  pre: (preProps) => {
    const props = preToCodeBlock(preProps);

    if (props) {
      return <Code {...props} />;
    }

    return <pre {...preProps} />;
  },
  inlineCode: (props) => <code className="inline-code" {...props} />,
  table: ({ children, ...rest }) => (
    <div style={{ overflowX: `auto` }}>
      <table {...rest}>{children}</table>
    </div>
  ),
  ...shortcodes
};

export function wrapPageElement({ element }) {
  return <MDXProvider components={components}>{element}</MDXProvider>;
}
