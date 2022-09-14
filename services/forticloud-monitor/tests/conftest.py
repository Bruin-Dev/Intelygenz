from unittest.mock import Mock

import shortuuid

shortuuid.uuid = Mock(return_value="any_uuid")

