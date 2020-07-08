import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import Modal from './Modal';

describe('Modal tests', () => {
  it('renders correctly', () => {
    const { queryByTestId } = render(
      <Modal
        buttonText="XXX"
        titleModal="XXX?"
        textModal="XXX_text"
        callbackResult={() => {}}
      />
    );
    expect(queryByTestId('modal-component')).toBeTruthy();
    expect(queryByTestId('modal-component-open-button')).toBeTruthy();
  });

  it('Open modal and click in confirm button', () => {
    const mockFunc = jest.fn();

    const { getByText, queryByTestId } = render(
      <Modal
        buttonText="XXX"
        titleModal="XXX?"
        textModal="XXX_text"
        callbackResult={mockFunc}
      />
    );
    const button = getByText('XXX');
    fireEvent.click(button);

    const confirmButton = queryByTestId('modal-component-confirm-button');
    fireEvent.click(confirmButton);

    expect(mockFunc).toHaveBeenCalledWith(true);
  });

  it('Open modal and click in cancel button', () => {
    const mockFunc = jest.fn();

    const { getByText, queryByTestId } = render(
      <Modal
        buttonText="XXX"
        titleModal="XXX?"
        textModal="XXX_text"
        callbackResult={mockFunc}
      />
    );
    const button = getByText('XXX');
    fireEvent.click(button);

    expect(queryByTestId('modal-component')).toHaveClass(
      `modal modal-active fixed w-full h-full top-0 left-0 flex items-center justify-center`
    );

    const confirmButton = queryByTestId('modal-component-cancel-button');
    fireEvent.click(confirmButton);

    expect(queryByTestId('modal-component')).toHaveClass(
      `modal opacity-0 pointer-events-none fixed w-full h-full top-0 left-0 flex items-center justify-center`
    );
  });

  it('Open modal and click in cancel general', () => {
    const mockFunc = jest.fn();

    const { getByText, queryByTestId } = render(
      <Modal
        buttonText="XXX"
        titleModal="XXX?"
        textModal="XXX_text"
        callbackResult={mockFunc}
      />
    );
    const button = getByText('XXX');
    fireEvent.click(button);

    expect(queryByTestId('modal-component')).toHaveClass(
      `modal modal-active fixed w-full h-full top-0 left-0 flex items-center justify-center`
    );

    const confirmButton = queryByTestId('modal-component-general-close');
    fireEvent.click(confirmButton);

    expect(queryByTestId('modal-component')).toHaveClass(
      `modal opacity-0 pointer-events-none fixed w-full h-full top-0 left-0 flex items-center justify-center`
    );
  });
  it('Open modal and click in cancel general(container inside modal)', () => {
    const mockFunc = jest.fn();

    const { getByText, queryByTestId } = render(
      <Modal
        buttonText="XXX"
        titleModal="XXX?"
        textModal="XXX_text"
        callbackResult={mockFunc}
      />
    );
    const button = getByText('XXX');
    fireEvent.click(button);

    expect(queryByTestId('modal-component')).toHaveClass(
      `modal modal-active fixed w-full h-full top-0 left-0 flex items-center justify-center`
    );

    const confirmButton = queryByTestId('modal-component-container-close');
    fireEvent.click(confirmButton);

    expect(queryByTestId('modal-component')).toHaveClass(
      `modal opacity-0 pointer-events-none fixed w-full h-full top-0 left-0 flex items-center justify-center`
    );
  });
});
