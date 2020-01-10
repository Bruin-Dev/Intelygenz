import logging
import sys


class OutageUtils:

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
        is_faulty_edge = self.is_faulty_edge(edge_status["edges"]["edgeState"])
        is_there_any_faulty_link = any(
            self.is_faulty_link(link_status['link']['state'])
            for link_status in edge_status['links']
        )

        return is_faulty_edge or is_there_any_faulty_link

    def is_faulty_edge(self, edge_state: str):
        return edge_state == 'OFFLINE'

    def is_faulty_link(self, link_state: str):
        return link_state == 'DISCONNECTED'
