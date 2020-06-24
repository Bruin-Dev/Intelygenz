from datetime import datetime

from apscheduler.util import undefined
from pytz import timezone


class CtsRepository:

    def __init__(self, cts_client, logger, scheduler, config):
        self._cts_client = cts_client
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._cts_excluded_fields = [
            'Billing_Invoice_Date__c',
            'Billing_Invoice_Number__c',
            'Billing_Total__c',
            'Carrier__c',
            'Carrier_ID_Num__c',
            'Finance_Notes__c',
            'Lift_Delivery_Date__c',
            'Lift_Release_Date__c',
            'Lift_Vendor__c',
            'P1__c',
            'P10__c',
            'P10A__c',
            'P11__c',
            'P11A__c',
            'P12__c',
            'P12A__c',
            'P13__c',
            'P13A__c',
            'P14__c',
            'P14A__c',
            'P15__c',
            'P15A__c',
            'P1A__c',
            'P2__c',
            'P2A__c',
            'P3__c',
            'P3A__c',
            'P4__c',
            'P4A__c',
            'P5__c',
            'P5A__c',
            'P6__c',
            'P6A__c',
            'P7__c',
            'P7A__c',
            'P8__c',
            'P8A__c',
            'P9__c',
            'P9A__c',
            'Trained_3rd_Party__c',
            'Release_Number__c',
            'Resource_Trained__c',
        ]
        self._cts_excluded_fields_minimun_fields = [
            'Trained_3rd_Party__c',
            'Service_Order__c',
            'Project_Name__c',
            'Location__c',
            'Release_Number__c',
            'Resource__c',
            'Parent_Account_Associated__c',
            'Service_Order__c',
            'Project_Name__c',
            'State__c'
        ]
        self._cts_fields = [
            'Id',
            'Name',
            'API_Resource_Name__c',
            'Billing_Invoice_Date__c',
            'Billing_Invoice_Number__c',
            'Billing_Total__c',
            'Carrier__c',
            'Carrier_ID_Num__c',
            'Check_In_Date__c',
            'Check_Out_Date__c',
            'City__c',
            'Confirmed__c',
            'Country__c',
            'Trained_3rd_Party__c',
            'Description__c',
            'Duration_Onsite__c',
            'Early_Start__c',
            'Ext_Ref_Num__c',
            'Finance_Notes__c',
            'Issue_Summary__c',
            'Lift_Delivery_Date__c',
            'Lift_Release_Date__c',
            'Lift_Vendor__c',
            'Local_Site_Time__c',
            'Account__c',
            'Lookup_Location_Owner__c',
            'On_Site_Elapsed_Time__c',
            'On_Time_Auto__c',
            'Open_Date__c',
            'P1__c',
            'P10__c',
            'P10A__c',
            'P11__c',
            'P11A__c',
            'P12__c',
            'P12A__c',
            'P13__c',
            'P13A__c',
            'P14__c',
            'P14A__c',
            'P15__c',
            'P15A__c',
            'P1A__c',
            'P2__c',
            'P2A__c',
            'P3__c',
            'P3A__c',
            'P4__c',
            'P4A__c',
            'P5__c',
            'P5A__c',
            'P6__c',
            'P6A__c',
            'P7__c',
            'P7A__c',
            'P8__c',
            'P8A__c',
            'P9__c',
            'P9A__c',
            'Parent_Account_Associated__c',
            'Service_Order__c',
            'Project_Name__c',
            'Location__c',
            'Release_Number__c',
            'Resource__c',
            'Resource_Assigned_Timestamp__c',
            'Resource_Email__c',
            'Resource_Phone_Number__c',
            'Site_Notes__c',
            'Site_Status__c',
            'Special_Shipping_Instructions__c',
            'State__c',
            'Street__c',
            'Status__c',
            'Resource_Trained__c',
            'Service_Type__c',
            'Zip__c']
        self._cts_all_fields = [f for f in self._cts_fields if f not in self._cts_excluded_fields_minimun_fields]
        self._cts_common_fields = [f for f in self._cts_fields if f not in self._cts_excluded_fields]
        self._cts_query_fields = ','.join(self._cts_common_fields)
        self._cts_query_all_fields = ','.join(self._cts_all_fields)

    def login_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: logging in cts api')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.CTS_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._cts_client.login, 'interval',
                                minutes=self._config.CTS_CONFIG['login_ttl'],
                                next_run_time=next_run_time, replace_existing=True,
                                id='login')

    def create_dispatch(self, payload):
        response = self._cts_client.create_dispatch(payload)
        return response

    def get_dispatch(self, dispatch_id):
        response = self._cts_client.get_dispatch(dispatch_id, self._cts_query_all_fields)
        return response

    def get_all_dispatches(self):
        response = self._cts_client.get_all_dispatches(self._cts_query_all_fields)
        return response

    def update_dispatch(self, dispatch_id, payload):
        response = self._cts_client.update_dispatch(dispatch_id, payload)
        return response
