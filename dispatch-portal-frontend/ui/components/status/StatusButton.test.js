import React from 'react';
import { render } from '@testing-library/react';
import { StatusButton, TYPES_STATUS } from './StatusButton';

describe('Status Button test', () => {
  it('renders correctly', () => {
    const { queryByTestId } = render(<StatusButton />);
    expect(queryByTestId('statusButton-component')).toBeTruthy();
  });

  it(`check differents status:${TYPES_STATUS.newDispatch.value}`, () => {
    const { getByTestId } = render(
      <StatusButton status={TYPES_STATUS.newDispatch.value} />
    );

    const button = expect(getByTestId('statusButton-component'));
    button.toHaveTextContent(TYPES_STATUS.newDispatch.value);

    button.toHaveClass(TYPES_STATUS.newDispatch.color);
  });

  it(`check differents status:${TYPES_STATUS.requestConfirmed.value}`, () => {
    const { getByTestId } = render(
      <StatusButton status={TYPES_STATUS.requestConfirmed.value} />
    );

    const button = expect(getByTestId('statusButton-component'));
    button.toHaveTextContent(TYPES_STATUS.requestConfirmed.value);

    button.toHaveClass(TYPES_STATUS.requestConfirmed.color);
  });

  it(`check differents status:${TYPES_STATUS.techArrived.value}`, () => {
    const { getByTestId } = render(
      <StatusButton status={TYPES_STATUS.techArrived.value} />
    );

    const button = expect(getByTestId('statusButton-component'));
    button.toHaveTextContent(TYPES_STATUS.techArrived.value);

    button.toHaveClass(TYPES_STATUS.techArrived.color);
  });

  it(`check differents status:${TYPES_STATUS.repairCompleted.value}`, () => {
    const { getByTestId } = render(
      <StatusButton status={TYPES_STATUS.repairCompleted.value} />
    );

    const button = expect(getByTestId('statusButton-component'));
    button.toHaveTextContent(TYPES_STATUS.repairCompleted.value);

    button.toHaveClass(TYPES_STATUS.repairCompleted.color);
  });

  // CTS status
  it(`check differents status:${TYPES_STATUS.open.value}`, () => {
    const { getByTestId } = render(
      <StatusButton status={TYPES_STATUS.open.value} />
    );

    const button = expect(getByTestId('statusButton-component'));
    button.toHaveTextContent(TYPES_STATUS.open.value);

    button.toHaveClass(TYPES_STATUS.open.color);
  });

  it(`check differents status:${TYPES_STATUS.scheduled.value}`, () => {
    const { getByTestId } = render(
      <StatusButton status={TYPES_STATUS.scheduled.value} />
    );

    const button = expect(getByTestId('statusButton-component'));
    button.toHaveTextContent(TYPES_STATUS.scheduled.value);

    button.toHaveClass(TYPES_STATUS.scheduled.color);
  });

  it(`check differents status:${TYPES_STATUS.onSite.value}`, () => {
    const { getByTestId } = render(
      <StatusButton status={TYPES_STATUS.onSite.value} />
    );

    const button = expect(getByTestId('statusButton-component'));
    button.toHaveTextContent(TYPES_STATUS.onSite.value);

    button.toHaveClass(TYPES_STATUS.onSite.color);
  });

  it(`check differents status:${TYPES_STATUS.completed.value}`, () => {
    const { getByTestId } = render(
      <StatusButton status={TYPES_STATUS.completed.value} />
    );

    const button = expect(getByTestId('statusButton-component'));
    button.toHaveTextContent(TYPES_STATUS.completed.value);

    button.toHaveClass(TYPES_STATUS.completed.color);
  });

  it(`check differents status:${TYPES_STATUS.completePendingCollateral.value}`, () => {
    const { getByTestId } = render(
      <StatusButton status={TYPES_STATUS.completePendingCollateral.value} />
    );

    const button = expect(getByTestId('statusButton-component'));
    button.toHaveTextContent(TYPES_STATUS.completePendingCollateral.value);

    button.toHaveClass(TYPES_STATUS.completePendingCollateral.color);
  });

  it(`check differents status:${TYPES_STATUS.cancelled.value}`, () => {
    const { getByTestId } = render(
      <StatusButton status={TYPES_STATUS.cancelled.value} />
    );

    const button = expect(getByTestId('statusButton-component'));
    button.toHaveTextContent(TYPES_STATUS.cancelled.value);

    button.toHaveClass(TYPES_STATUS.cancelled.color);
  });
});
