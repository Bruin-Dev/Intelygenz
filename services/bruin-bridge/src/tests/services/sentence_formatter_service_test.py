from application.services.sentence_formatter import SentenceFormatter


def email_marked_sentence_is_properly_formatted_test():
    sentence_formatter = SentenceFormatter(_subject="any_username")
    sentence = sentence_formatter.email_marked_as("any_status")
    assert sentence == "Marked as any_status by any_username"
