import React from 'react';
import { ButtonExample } from './Button';

export default {
  title: 'Button',
  component: ButtonExample
};

export const Text = () => (
  <ButtonExample>
    <span>Hello world!</span>
  </ButtonExample>
);

export const Emoji = () => (
  <ButtonExample>
    <span role="img" aria-label="so cool">
      😀 😎 👍 💯
    </span>
  </ButtonExample>
);
