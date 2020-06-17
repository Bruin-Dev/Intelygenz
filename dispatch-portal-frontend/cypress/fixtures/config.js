import { mockLitSingleDispatch } from '../../services/mocks/data/lit/single-dispatch.mock';
import { formDataNewDispatch } from '../../services/mocks/data/new-dispatch.mock';
import { userLoginSucess } from '../../services/mocks/data/userData.mocks';

export default {
  userEmail: userLoginSucess.email,
  userPassword: userLoginSucess.password,
  dispatch: formDataNewDispatch,
  getDispatch: {
    ...mockLitSingleDispatch
  }
};
