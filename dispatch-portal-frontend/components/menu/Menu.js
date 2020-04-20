import PropTypes from 'prop-types';
import { useRouter } from 'next/router';
import { Routes } from '../../config/routes';
import { TOKEN_STORAGE_KEY } from '../../services/auth/login.service';
import './Menu.scss';

function Menu({ authToken }) {
  const router = useRouter();

  const logOut = () => {
    document.cookie = `${TOKEN_STORAGE_KEY}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT`;
    router.push(Routes.LOGIN());
  };

  return (
    <div className="wrapper-menu">
      <ul>
        <li className="logo">
          <a href={Routes.BASE()} className="logo__link">
            <svg xmlns="http://www.w3.org/2000/svg" width="100" height="32">
              <g id="Symbols" stroke="none" strokeWidth="1" fill="none">
                <g id="Nav" transform="translate(0 -9)" fill="#FEFEFE">
                  <g transform="translate(0 9)" id="Group">
                    <path
                      d="M77.483 12.57h6.444c.35-1.944-.262-3.53-2.582-3.53-2.097 0-3.384 1.586-3.862 3.53zm7.128 6.045l1.348 3-.055.314C83.9 22.673 81.715 23 79.557 23c-5.54 0-9.168-3.27-8.16-8.843 1.01-5.57 5.362-8.81 10.583-8.81 6.217 0 7.67 4.439 6.76 9.458l-.193 1.068H76.951c-.099 2.331 1.504 3.24 4.34 3.24 1.011 0 2.139-.148 3.32-.498zM92.204 0l-4.101 22.61h5.8L98 0h-5.796zM42.482 9.04c-2.095 0-3.379 1.586-3.86 3.53h6.445c.347-1.944-.263-3.53-2.585-3.53zM72.31 4.475L69.03 22.61h-5.993l2.04-11.281 6.126-1.495H57.547l-.632 3.49-.494 2.708c-.367 2.043-.066 3.096 1.53 3.096l1.555 3.544c-1.12.132-2.25.327-3.702.327-5.183 0-6.024-2.3-5.297-6.318l1.24-6.865-1.92-.008c.39 1.474.379 3.195.052 4.996l-.196 1.068H38.088c-.098 2.331 1.505 3.24 4.34 3.24.938 0 1.971-.124 3.059-.42l1.47 3.266C44.973 22.681 42.82 23 40.694 23c-5.54 0-9.168-3.27-8.156-8.843 1.006-5.57 5.36-8.81 10.578-8.81 3.825 0 5.843 1.681 6.62 4.143l.23-.934 9.09-6.984-.772 4.164h7.806l.227-1.262h-3.879l.81-4.472H78.66l-.808 4.472H72.31zM25.352.002l-7.708 15.027h-.067L15.529.002H6.092L2 22.61h5.859l3.018-17.36h.062l2.333 17.36h5.51l8.876-17.36h.062l-3.238 17.36h5.864L34.439 0h-9.087z"
                      id="Fill-1"
                    />
                    <path id="Fill-3" d="M0 32l72-7H1.288z" />
                    <path
                      d="M96.94 20.388h.306c.347 0 .642-.118.642-.424 0-.215-.167-.432-.642-.432a2.04 2.04 0 00-.306.019v.837zm0 1.368h-.423v-2.47c.222-.03.434-.06.75-.06.402 0 .664.078.823.187.158.108.242.275.242.512 0 .326-.232.522-.516.6v.021c.23.039.39.236.442.599.064.385.127.533.17.611h-.444c-.064-.078-.127-.304-.18-.63-.062-.315-.231-.433-.57-.433h-.294v1.063zm.443-3.16c-1.044 0-1.898.836-1.898 1.87 0 1.053.854 1.88 1.908 1.88a1.867 1.867 0 001.9-1.869 1.882 1.882 0 00-1.9-1.881h-.01zm.01-.345c1.298 0 2.333.985 2.333 2.215 0 1.252-1.035 2.226-2.343 2.226-1.297 0-2.352-.974-2.352-2.226 0-1.23 1.055-2.215 2.352-2.215h.01z"
                      id="Fill-5"
                    />
                  </g>
                </g>
              </g>
            </svg>
          </a>
        </li>
        <li>
          <a href={Routes.BASE()}>Dashboard</a>
        </li>
        <li>
          <a href={Routes.NEW_DISPATCH()}>New Dispatch</a>
        </li>
        <li className="right">
          <button type="button" onClick={logOut}>
            Log out
          </button>
        </li>
      </ul>
    </div>
  );
}

Menu.propTypes = {
  authToken: PropTypes.string
};

export default Menu;
