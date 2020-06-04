import { mockLitSingleDispatch } from '../../services/mocks/single-dispatch.mock';
import { formDataNewDispatch } from '../../services/mocks/new-dispatch.mock';
import { userLoginSucess } from '../../services/mocks/userData.mocks';

export default {
  userEmail: userLoginSucess.email,
  userPassword: userLoginSucess.password,
  dispatch: formDataNewDispatch,
  getDispatch: {
    ...mockLitSingleDispatch
  }
};
