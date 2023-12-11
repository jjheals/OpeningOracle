import { Outlet, Link } from "react-router-dom";

import "./Header.css"

function HeaderTest() {
  return (
    <>
      <div className='header'>
        <div>
          <p className="title">OpeningOracle</p>
        </div>
        <div>
          <Link className="link" to="/">Home</Link>
        </div>
        <div>
          <a className="link" href="https://github.com/jjheals/OpeningOracle/">GitHub</a>
        </div>
        <div>
          <Link className="link" to="/about">About</Link>
        </div>
      </div>

      <Outlet />
    </>
  )
};

export default HeaderTest;