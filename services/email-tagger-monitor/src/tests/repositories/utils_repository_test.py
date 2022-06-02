from application.repositories.utils_repository import UtilsRepository


class TestUtilsRepository:
    def convert_dict_to_snake_case_test(self):
        payload = {
            "Body": {"Second": 1234, "Third": [{"Test": 1, "More": 2}, {"Test": 2, "More": 3}]},
            "MultiWord": "TEST",
        }
        expected_response = {
            "body": {"second": 1234, "third": [{"test": 1, "more": 2}, {"test": 2, "more": 3}]},
            "multi_word": "TEST",
        }

        utils = UtilsRepository()

        actual_response = utils.convert_dict_to_snake_case(payload)

        assert actual_response == expected_response
