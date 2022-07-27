class ServiceNowRepository:
    def __init__(self, servicenow_client):
        self._servicenow_client = servicenow_client

    async def report_incident(self, host, gateway, summary, note, link):
        payload = {
            "u_host_name": host,
            "u_vcg": gateway,
            "u_short_description": summary,
            "u_description": note,
            "u_link": link,
        }
        return await self._servicenow_client.report_incident(payload)
