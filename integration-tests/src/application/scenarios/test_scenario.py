import logging

from application.clients import bruin_webhooks
from application.handler import WillReturn
from application.scenario import Scenario
from application.scenarios.models.email import Email
from application.servers.grpc.email_tagger.email_tagger import EmailTaggerService, default_prediction_response
from application.servers.grpc.rta.rta import RtaService
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class TestScenario(Scenario):
    name: str = "test_scenario"

    async def run(self):
        # given
        prediction_response = default_prediction_response()
        email_id = hash("any_email_id")
        self.given(EmailTaggerService.path("GetPrediction"), WillReturn(prediction_response))

        # when
        await bruin_webhooks.notify_email(Email(Id=email_id))

        # then
        try:
            await self.route(RtaService.path("SaveOutputs")).was_reached(25.0)
        except TimeoutError as e:
            return self.failed(reason=str(e))

        return self.passed()
