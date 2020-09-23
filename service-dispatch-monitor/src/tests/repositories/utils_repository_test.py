import datetime


from application.repositories.utils_repository import UtilsRepository


class TestUtilsRepository:
    def get_first_element_matching_with_match_test(self):
        payload = range(0, 11)

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = UtilsRepository.get_first_element_matching(iterable=payload, condition=cond)
        expected = 5

        assert result == expected

    def get_first_element_matching_with_no_match_test(self):
        payload = [0] * 10
        fallback_value = 42

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = UtilsRepository.get_first_element_matching(iterable=payload, condition=cond, fallback=fallback_value)

        assert result == fallback_value

    def get_last_element_matching_with_match_test(self):
        payload = range(0, 11)

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = UtilsRepository.get_last_element_matching(iterable=payload, condition=cond)
        expected = 10

        assert result == expected

    def get_last_element_matching_with_no_match_test(self):
        payload = [0] * 10
        fallback_value = 42

        def is_divisible_by_5(num):
            return num % 5 == 0

        def is_not_zero(num):
            return num != 0

        def cond(num):
            return is_divisible_by_5(num) and is_not_zero(num)

        result = UtilsRepository.get_last_element_matching(iterable=payload, condition=cond, fallback=fallback_value)

        assert result == fallback_value

    def get_diff_hours_between_datetimes_test(self):
        data1 = datetime.datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')
        data2 = datetime.datetime.strptime('2020-03-16 6:00PM', '%Y-%m-%d %I:%M%p')
        data3 = datetime.datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p')
        data4 = datetime.datetime.strptime('2020-03-17 4:00PM', '%Y-%m-%d %I:%M%p')

        hours_2 = UtilsRepository.get_diff_hours_between_datetimes(data2, data1)
        hours_24 = UtilsRepository.get_diff_hours_between_datetimes(data4, data3)
        assert hours_2 == 2.0
        assert hours_24 == 24.0

        hours_2 = UtilsRepository.get_diff_hours_between_datetimes(data1, data2)
        hours_24 = UtilsRepository.get_diff_hours_between_datetimes(data3, data4)
        assert hours_2 == 2.0
        assert hours_24 == 24.0

        data5 = datetime.datetime.strptime('2020-03-16 10:00AM', '%Y-%m-%d %I:%M%p')
        data6 = datetime.datetime.strptime('2020-03-16 10:30AM', '%Y-%m-%d %I:%M%p')

        hours_30_min = UtilsRepository.get_diff_hours_between_datetimes(data5, data6)
        assert hours_30_min == 0.5

        data7 = datetime.datetime.strptime('2020-03-16 10:00AM', '%Y-%m-%d %I:%M%p')
        data8 = datetime.datetime.strptime('2020-03-16 9:30PM', '%Y-%m-%d %I:%M%p')

        hours_11h_30_min = UtilsRepository.get_diff_hours_between_datetimes(data7, data8)
        assert hours_11h_30_min == 11.5

        data9 = datetime.datetime.strptime('2020-03-16 10:00AM', '%Y-%m-%d %I:%M%p')
        data10 = datetime.datetime.strptime('2020-03-16 8:55PM', '%Y-%m-%d %I:%M%p')

        hours_10h_55_min = UtilsRepository.get_diff_hours_between_datetimes(data9, data10)
        assert hours_10h_55_min == 10.92

    def find_note_test(self, lit_dispatch_monitor, ticket_details):
        expected_note_found = {
            "noteId": 70805300,
            "noteValue": "#*Automation Engine*# DIS37405\nDispatch Management - Dispatch Requested\n\n"
                         "Please see the summary below.\n--\n"
                         "Dispatch Number:  "
                         "[DIS37405|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS37405] "
                         "\nDate of Dispatch: 2019-11-14\nTime of Dispatch (Local): 6PM-8PM\n"
                         "Time Zone (Local): Pacific Time\n\n"
                         "Location Owner/Name: Red Rose Inn\n"
                         "Address: 123 Fake Street, Pleasantown, CA, 99088\nOn-Site Contact: Jane Doe\n"
                         "Phone: +1 666 6666 666\n\n"
                         "Issues Experienced:\nDevice is bouncing constantly TEST LUNES\n"
                         "Arrival Instructions: "
                         "When arriving to the site call HOLMDEL NOC for telematic assistance\n"
                         "Materials Needed:\nLaptop, cable, tuner, ladder,internet hotspot\n\n"
                         "Requester\nName: Karen Doe\nPhone: +1 666 6666 666\n"
                         "Email: karen.doe@mettel.net\nDepartment: Customer Care",
            "serviceNumber": [
                "4664325"
            ],
            "createdDate": "2020-05-28T06:06:40.27-04:00",
            "creator": None
        }
        ticket_notes = ticket_details.get('body').get('ticketNotes')
        watermark_to_find = lit_dispatch_monitor.DISPATCH_REQUESTED_WATERMARK
        result = UtilsRepository.find_note(ticket_notes, watermark_to_find)
        assert result == expected_note_found

    def find_dispatch_number_watermark_ok_test(self, ticket_details):
        dispatch_number = "DIS37405"
        watermark = '#*Automation Engine*#'
        dispatch_note = ticket_details['body']["ticketNotes"][1]

        result = UtilsRepository.find_dispatch_number_watermark(dispatch_note, dispatch_number, watermark)

        assert result == dispatch_number

    def find_dispatch_number_watermark_ko_test(self, ticket_details):
        dispatch_number = "DIS37405"
        watermark = '#*Automation Engine*#'
        dispatch_note = ticket_details['body']["ticketNotes"][2]

        result = UtilsRepository.find_dispatch_number_watermark(dispatch_note, dispatch_number, watermark)

        assert result == ''
