import logging
import sys
import re


class OutageRepository:

    logger = None

    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger('autoresolve')
            logger.setLevel(logging.DEBUG)
            log_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s: %(module)s: %(levelname)s: %(message)s')
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)
        self.logger = logger

    def is_there_an_outage(self, edge_status):
        is_faulty_edge = self.is_faulty_edge(edge_status["edgeState"])
        is_there_any_faulty_link = any(
            self.is_faulty_link(link_status['linkState'])
            for link_status in edge_status['links']
        )

        return is_faulty_edge or is_there_any_faulty_link

    def is_faulty_edge(self, edge_state: str):
        return edge_state == 'OFFLINE'

    def is_faulty_link(self, link_state: str):
        return link_state == 'DISCONNECTED'

    def is_any_link_disconnected(self, links: list) -> bool:
        return any(self.find_disconnected_links(links))

    def find_disconnected_links(self, links: list) -> list:
        return [link for link in links if self.is_faulty_link(link['linkState'])]

    def is_outage_ticket_detail_auto_resolvable(self, ticket_notes: list,
                                                serial_number: str,
                                                max_autoresolves: int) -> bool:
        regex = re.compile(r"^#\*(Automation Engine|MetTel's IPA)\*#\nAuto-resolving detail for serial")
        times_autoresolved = 0

        for ticket_note in ticket_notes:
            note_value = ticket_note['noteValue']
            is_autoresolve_note = bool(regex.match(note_value))
            is_note_related_to_serial = serial_number in ticket_note['serviceNumber']
            times_autoresolved += int(is_autoresolve_note and is_note_related_to_serial)

            if times_autoresolved >= max_autoresolves:
                return False

        return True
