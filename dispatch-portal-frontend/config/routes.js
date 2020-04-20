import { config } from './config';

export const Routes = {
  BASE: () => `${config.basePath}`,
  DISPATCH: () => `${config.basePath}dispatch`,
  NEW_DISPATCH: () => `${config.basePath}new-dispatch`,
  LOGIN: () => `${config.basePath}login`
};
