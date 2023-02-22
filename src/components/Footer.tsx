import React from 'react';

export default function Footer() {
  
  const currentYear = new Date().getFullYear();

  return (
    <>
      &copy; {currentYear} Coffeebank ☕🏦 <br />
      <a href="https://coffeebank.github.io/" target="_blank" rel="noopener">Home</a>&ensp;
      <a href="https://github.com/coffeebank/coffee-cogs/" target="_blank" rel="noopener">GitHub</a>&ensp;
      <a href="https://github.com/coffeebank/coffee-cogs/blob/master/LICENSE" target="_blank" rel="noopener">License</a>
    </>
  )
}
