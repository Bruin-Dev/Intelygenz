import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import { RouterContext } from 'next/dist/next-server/lib/router-context';
import { toHaveClass } from '@testing-library/jest-dom';
import Menu from './Menu';
import { Routes } from '../../config/routes';

export function withTestRouter(tree, router) {
  const {
    route = '',
    pathname = '',
    query = {},
    asPath = '',
    push = async () => true,
    replace = async () => true,
    reload = () => null,
    back = () => null,
    prefetch = async () => undefined,
    beforePopState = () => null,
    isFallback = false,
    events = {
      on: () => null,
      off: () => null,
      emit: () => null
    }
  } = router;

  return (
    <RouterContext.Provider
      value={{
        route,
        pathname,
        query,
        asPath,
        push,
        replace,
        reload,
        back,
        prefetch,
        beforePopState,
        isFallback,
        events
      }}
    >
      {tree}
    </RouterContext.Provider>
  );
}

describe('Menu tests', () => {
  it('renders correctly', () => {
    const { queryByTestId } = render(<Menu />);
    expect(queryByTestId('menu-component')).toBeTruthy();
  });

  it('Check logOut button', () => {
    const push = jest.fn();

    const component = withTestRouter(<Menu />, {
      push,
      pathname: '/',
      asPath: '/'
    });

    const { getByText } = render(component);
    const button = getByText('Log out');

    fireEvent.click(button);

    expect(push).toHaveBeenCalledWith(Routes.LOGIN());
  });

  it('Check Open menu button', () => {
    const { getByTestId } = render(<Menu />);
    const button = getByTestId('menu-mobile-button');
    const menuContainer = getByTestId('menu-container');

    fireEvent.click(button);

    expect(menuContainer).toHaveClass(
      `w-full block flex-grow lg:flex lg:items-center lg:w-auto`
    );
  });
});
