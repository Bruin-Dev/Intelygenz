# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: public_input.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x12public_input.proto\x12\nentrypoint"(\n\x03Tag\x12\x0c\n\x04type\x18\x01 \x01(\t\x12\x13\n\x0bprobability\x18\x02 \x01(\x02"\xf7\x01\n\x05\x45mail\x12\x10\n\x08\x65mail_id\x18\x01 \x01(\t\x12\x11\n\tparent_id\x18\x02 \x01(\t\x12\x11\n\tclient_id\x18\x03 \x01(\t\x12\x0f\n\x07subject\x18\x04 \x01(\t\x12\x0c\n\x04\x62ody\x18\x05 \x01(\t\x12\x14\n\x0c\x66rom_address\x18\x06 \x01(\t\x12\n\n\x02to\x18\x07 \x03(\t\x12\n\n\x02\x63\x63\x18\x08 \x01(\t\x12\x0c\n\x04\x64\x61te\x18\t \x01(\t\x12\x1c\n\x03tag\x18\n \x01(\x0b\x32\x0f.entrypoint.Tag\x12\x1c\n\x14is_auto_reply_answer\x18\x0b \x01(\x08\x12\x1f\n\x17\x61uto_reply_answer_delay\x18\x0c \x01(\x02"\x83\x01\n\x15PreprocessEmailFields\x12\x17\n\x0fsubject_no_html\x18\x01 \x01(\t\x12\x14\n\x0c\x62ody_no_html\x18\x02 \x01(\t\x12\x1e\n\x16subject_mlp_classifier\x18\x03 \x01(\t\x12\x1b\n\x13\x62ody_mlp_classifier\x18\x04 \x01(\t"u\n\x15PreprocessEmailOutput\x12 \n\x05\x65mail\x18\x01 \x01(\x0b\x32\x11.entrypoint.Email\x12:\n\x0fprocessed_email\x18\x02 \x01(\x0b\x32!.entrypoint.PreprocessEmailFields"\xc0\x01\n\x1b\x45xtractServiceNumbersOutput\x12 \n\x05\x65mail\x18\x01 \x01(\x0b\x32\x11.entrypoint.Email\x12:\n\x0fprocessed_email\x18\x02 \x01(\x0b\x32!.entrypoint.PreprocessEmailFields\x12!\n\x19potential_service_numbers\x18\x03 \x03(\t\x12 \n\x18potential_ticket_numbers\x18\x04 \x03(\t"\xec\x01\n\x1f\x43lassifyOutageVsAffectingFields\x12\x17\n\x0fpredicted_class\x18\x01 \x01(\t\x12\'\n\x1fpredicted_class_voovas_vs_other\x18\x02 \x01(\t\x12\x33\n+predicted_class_voovas_vs_other_probability\x18\x03 \x01(\x02\x12"\n\x1apredicted_class_voo_vs_vas\x18\x04 \x01(\t\x12.\n&predicted_class_voo_vs_vas_probability\x18\x05 \x01(\x02"\x89\x02\n\x1f\x43lassifyOutageVsAffectingOutput\x12 \n\x05\x65mail\x18\x01 \x01(\x0b\x32\x11.entrypoint.Email\x12:\n\x0fprocessed_email\x18\x02 \x01(\x0b\x32!.entrypoint.PreprocessEmailFields\x12!\n\x19potential_service_numbers\x18\x03 \x03(\t\x12\x43\n\x0e\x63lassification\x18\x04 \x01(\x0b\x32+.entrypoint.ClassifyOutageVsAffectingFields\x12 \n\x18potential_ticket_numbers\x18\x05 \x03(\t"\xdb\x02\n\x13PrepareOutputFields\x12\x1e\n\x16tagger_threshold_value\x18\x01 \x01(\x02\x12!\n\x19tagger_is_below_threshold\x18\x02 \x01(\x08\x12"\n\x1arta_model1_threshold_value\x18\x03 \x01(\x02\x12%\n\x1drta_model1_is_below_threshold\x18\x04 \x01(\x08\x12"\n\x1arta_model2_threshold_value\x18\x05 \x01(\x02\x12%\n\x1drta_model2_is_below_threshold\x18\x06 \x01(\x08\x12\x13\n\x0bis_filtered\x18\x07 \x01(\x08\x12\x17\n\x0f\x66iltered_reason\x18\x08 \x01(\t\x12\x19\n\x11in_validation_set\x18\t \x01(\x08\x12"\n\x1avalidation_set_probability\x18\n \x01(\x02"5\n\x11PredictionRequest\x12 \n\x05\x65mail\x18\x01 \x01(\x0b\x32\x11.entrypoint.Email"\xb4\x01\n\x11OutputFilterFlags\x12!\n\x19tagger_is_below_threshold\x18\x01 \x01(\x08\x12%\n\x1drta_model1_is_below_threshold\x18\x02 \x01(\x08\x12%\n\x1drta_model2_is_below_threshold\x18\x03 \x01(\x08\x12\x13\n\x0bis_filtered\x18\x04 \x01(\x08\x12\x19\n\x11in_validation_set\x18\x05 \x01(\x08"\xa7\x01\n\x12PredictionResponse\x12!\n\x19potential_service_numbers\x18\x01 \x03(\t\x12\x17\n\x0fpredicted_class\x18\x02 \x01(\t\x12\x33\n\x0c\x66ilter_flags\x18\x03 \x01(\x0b\x32\x1d.entrypoint.OutputFilterFlags\x12 \n\x18potential_ticket_numbers\x18\x04 \x03(\t"b\n\x06Ticket\x12\x0f\n\x07site_id\x18\x01 \x01(\t\x12\x17\n\x0fservice_numbers\x18\x02 \x03(\t\x12\x11\n\tticket_id\x18\x03 \x01(\t\x12\x1b\n\x13not_creation_reason\x18\x04 \x01(\t"q\n\x0fValidatedTicket\x12\x11\n\tticket_id\x18\x01 \x01(\t\x12\x15\n\rticket_status\x18\x02 \x01(\t\x12\x10\n\x08\x63\x61tegory\x18\x03 \x01(\t\x12\x11\n\tcall_type\x18\x04 \x01(\t\x12\x0f\n\x07site_id\x18\x05 \x01(\t"\xa3\x08\n\x12SaveOutputsRequest\x12\x10\n\x08\x65mail_id\x18\x01 \x01(\t\x12]\n\x19service_numbers_sites_map\x18\x02 \x03(\x0b\x32:.entrypoint.SaveOutputsRequest.ServiceNumbersSitesMapEntry\x12!\n\x19validated_service_numbers\x18\x03 \x03(\t\x12+\n\x0ftickets_created\x18\x04 \x03(\x0b\x32\x12.entrypoint.Ticket\x12+\n\x0ftickets_updated\x18\x05 \x03(\x0b\x32\x12.entrypoint.Ticket\x12\x34\n\x18tickets_could_be_created\x18\x06 \x03(\x0b\x32\x12.entrypoint.Ticket\x12\x34\n\x18tickets_could_be_updated\x18\x07 \x03(\x0b\x32\x12.entrypoint.Ticket\x12\x35\n\x19tickets_cannot_be_created\x18\t \x03(\x0b\x32\x12.entrypoint.Ticket\x12$\n\x18validated_ticket_numbers\x18\n \x03(\tB\x02\x18\x01\x12]\n\x17\x62ruin_ticket_status_map\x18\x0b \x03(\x0b\x32\x38.entrypoint.SaveOutputsRequest.BruinTicketStatusMapEntryB\x02\x18\x01\x12\x62\n\x1a\x62ruin_ticket_call_type_map\x18\x0c \x03(\x0b\x32:.entrypoint.SaveOutputsRequest.BruinTicketCallTypeMapEntryB\x02\x18\x01\x12\x61\n\x19\x62ruin_ticket_category_map\x18\r \x03(\x0b\x32:.entrypoint.SaveOutputsRequest.BruinTicketCategoryMapEntryB\x02\x18\x01\x12\x36\n\x11validated_tickets\x18\x0e \x03(\x0b\x32\x1b.entrypoint.ValidatedTicket\x1a=\n\x1bServiceNumbersSitesMapEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a;\n\x19\x42ruinTicketStatusMapEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a=\n\x1b\x42ruinTicketCallTypeMapEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a=\n\x1b\x42ruinTicketCategoryMapEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01"&\n\x13SaveOutputsResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08"\x9e\x02\n!SaveCreatedTicketsFeedbackRequest\x12\x11\n\tticket_id\x18\x01 \x01(\t\x12\x10\n\x08\x65mail_id\x18\x02 \x01(\t\x12\x11\n\tparent_id\x18\x03 \x01(\t\x12\x11\n\tclient_id\x18\x04 \x01(\t\x12\x1c\n\x14real_service_numbers\x18\x05 \x03(\t\x12\x12\n\nreal_class\x18\x06 \x01(\t\x12L\n\x08site_map\x18\x07 \x03(\x0b\x32:.entrypoint.SaveCreatedTicketsFeedbackRequest.SiteMapEntry\x1a.\n\x0cSiteMapEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01"5\n"SaveCreatedTicketsFeedbackResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08"z\n SaveClosedTicketsFeedbackRequest\x12\x11\n\tticket_id\x18\x01 \x01(\t\x12\x11\n\tclient_id\x18\x02 \x01(\t\x12\x15\n\rticket_status\x18\x03 \x01(\t\x12\x19\n\x11\x63\x61ncelled_reasons\x18\x04 \x03(\t"4\n!SaveClosedTicketsFeedbackResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x32\xab\x03\n\nEntrypoint\x12P\n\rGetPrediction\x12\x1d.entrypoint.PredictionRequest\x1a\x1e.entrypoint.PredictionResponse"\x00\x12P\n\x0bSaveOutputs\x12\x1e.entrypoint.SaveOutputsRequest\x1a\x1f.entrypoint.SaveOutputsResponse"\x00\x12}\n\x1aSaveCreatedTicketsFeedback\x12-.entrypoint.SaveCreatedTicketsFeedbackRequest\x1a..entrypoint.SaveCreatedTicketsFeedbackResponse"\x00\x12z\n\x19SaveClosedTicketsFeedback\x12,.entrypoint.SaveClosedTicketsFeedbackRequest\x1a-.entrypoint.SaveClosedTicketsFeedbackResponse"\x00\x62\x06proto3'
)


_TAG = DESCRIPTOR.message_types_by_name["Tag"]
_EMAIL = DESCRIPTOR.message_types_by_name["Email"]
_PREPROCESSEMAILFIELDS = DESCRIPTOR.message_types_by_name["PreprocessEmailFields"]
_PREPROCESSEMAILOUTPUT = DESCRIPTOR.message_types_by_name["PreprocessEmailOutput"]
_EXTRACTSERVICENUMBERSOUTPUT = DESCRIPTOR.message_types_by_name["ExtractServiceNumbersOutput"]
_CLASSIFYOUTAGEVSAFFECTINGFIELDS = DESCRIPTOR.message_types_by_name["ClassifyOutageVsAffectingFields"]
_CLASSIFYOUTAGEVSAFFECTINGOUTPUT = DESCRIPTOR.message_types_by_name["ClassifyOutageVsAffectingOutput"]
_PREPAREOUTPUTFIELDS = DESCRIPTOR.message_types_by_name["PrepareOutputFields"]
_PREDICTIONREQUEST = DESCRIPTOR.message_types_by_name["PredictionRequest"]
_OUTPUTFILTERFLAGS = DESCRIPTOR.message_types_by_name["OutputFilterFlags"]
_PREDICTIONRESPONSE = DESCRIPTOR.message_types_by_name["PredictionResponse"]
_TICKET = DESCRIPTOR.message_types_by_name["Ticket"]
_VALIDATEDTICKET = DESCRIPTOR.message_types_by_name["ValidatedTicket"]
_SAVEOUTPUTSREQUEST = DESCRIPTOR.message_types_by_name["SaveOutputsRequest"]
_SAVEOUTPUTSREQUEST_SERVICENUMBERSSITESMAPENTRY = _SAVEOUTPUTSREQUEST.nested_types_by_name[
    "ServiceNumbersSitesMapEntry"
]
_SAVEOUTPUTSREQUEST_BRUINTICKETSTATUSMAPENTRY = _SAVEOUTPUTSREQUEST.nested_types_by_name["BruinTicketStatusMapEntry"]
_SAVEOUTPUTSREQUEST_BRUINTICKETCALLTYPEMAPENTRY = _SAVEOUTPUTSREQUEST.nested_types_by_name[
    "BruinTicketCallTypeMapEntry"
]
_SAVEOUTPUTSREQUEST_BRUINTICKETCATEGORYMAPENTRY = _SAVEOUTPUTSREQUEST.nested_types_by_name[
    "BruinTicketCategoryMapEntry"
]
_SAVEOUTPUTSRESPONSE = DESCRIPTOR.message_types_by_name["SaveOutputsResponse"]
_SAVECREATEDTICKETSFEEDBACKREQUEST = DESCRIPTOR.message_types_by_name["SaveCreatedTicketsFeedbackRequest"]
_SAVECREATEDTICKETSFEEDBACKREQUEST_SITEMAPENTRY = _SAVECREATEDTICKETSFEEDBACKREQUEST.nested_types_by_name[
    "SiteMapEntry"
]
_SAVECREATEDTICKETSFEEDBACKRESPONSE = DESCRIPTOR.message_types_by_name["SaveCreatedTicketsFeedbackResponse"]
_SAVECLOSEDTICKETSFEEDBACKREQUEST = DESCRIPTOR.message_types_by_name["SaveClosedTicketsFeedbackRequest"]
_SAVECLOSEDTICKETSFEEDBACKRESPONSE = DESCRIPTOR.message_types_by_name["SaveClosedTicketsFeedbackResponse"]
Tag = _reflection.GeneratedProtocolMessageType(
    "Tag",
    (_message.Message,),
    {
        "DESCRIPTOR": _TAG,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.Tag)
    },
)
_sym_db.RegisterMessage(Tag)

Email = _reflection.GeneratedProtocolMessageType(
    "Email",
    (_message.Message,),
    {
        "DESCRIPTOR": _EMAIL,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.Email)
    },
)
_sym_db.RegisterMessage(Email)

PreprocessEmailFields = _reflection.GeneratedProtocolMessageType(
    "PreprocessEmailFields",
    (_message.Message,),
    {
        "DESCRIPTOR": _PREPROCESSEMAILFIELDS,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.PreprocessEmailFields)
    },
)
_sym_db.RegisterMessage(PreprocessEmailFields)

PreprocessEmailOutput = _reflection.GeneratedProtocolMessageType(
    "PreprocessEmailOutput",
    (_message.Message,),
    {
        "DESCRIPTOR": _PREPROCESSEMAILOUTPUT,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.PreprocessEmailOutput)
    },
)
_sym_db.RegisterMessage(PreprocessEmailOutput)

ExtractServiceNumbersOutput = _reflection.GeneratedProtocolMessageType(
    "ExtractServiceNumbersOutput",
    (_message.Message,),
    {
        "DESCRIPTOR": _EXTRACTSERVICENUMBERSOUTPUT,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.ExtractServiceNumbersOutput)
    },
)
_sym_db.RegisterMessage(ExtractServiceNumbersOutput)

ClassifyOutageVsAffectingFields = _reflection.GeneratedProtocolMessageType(
    "ClassifyOutageVsAffectingFields",
    (_message.Message,),
    {
        "DESCRIPTOR": _CLASSIFYOUTAGEVSAFFECTINGFIELDS,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.ClassifyOutageVsAffectingFields)
    },
)
_sym_db.RegisterMessage(ClassifyOutageVsAffectingFields)

ClassifyOutageVsAffectingOutput = _reflection.GeneratedProtocolMessageType(
    "ClassifyOutageVsAffectingOutput",
    (_message.Message,),
    {
        "DESCRIPTOR": _CLASSIFYOUTAGEVSAFFECTINGOUTPUT,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.ClassifyOutageVsAffectingOutput)
    },
)
_sym_db.RegisterMessage(ClassifyOutageVsAffectingOutput)

PrepareOutputFields = _reflection.GeneratedProtocolMessageType(
    "PrepareOutputFields",
    (_message.Message,),
    {
        "DESCRIPTOR": _PREPAREOUTPUTFIELDS,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.PrepareOutputFields)
    },
)
_sym_db.RegisterMessage(PrepareOutputFields)

PredictionRequest = _reflection.GeneratedProtocolMessageType(
    "PredictionRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _PREDICTIONREQUEST,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.PredictionRequest)
    },
)
_sym_db.RegisterMessage(PredictionRequest)

OutputFilterFlags = _reflection.GeneratedProtocolMessageType(
    "OutputFilterFlags",
    (_message.Message,),
    {
        "DESCRIPTOR": _OUTPUTFILTERFLAGS,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.OutputFilterFlags)
    },
)
_sym_db.RegisterMessage(OutputFilterFlags)

PredictionResponse = _reflection.GeneratedProtocolMessageType(
    "PredictionResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _PREDICTIONRESPONSE,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.PredictionResponse)
    },
)
_sym_db.RegisterMessage(PredictionResponse)

Ticket = _reflection.GeneratedProtocolMessageType(
    "Ticket",
    (_message.Message,),
    {
        "DESCRIPTOR": _TICKET,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.Ticket)
    },
)
_sym_db.RegisterMessage(Ticket)

ValidatedTicket = _reflection.GeneratedProtocolMessageType(
    "ValidatedTicket",
    (_message.Message,),
    {
        "DESCRIPTOR": _VALIDATEDTICKET,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.ValidatedTicket)
    },
)
_sym_db.RegisterMessage(ValidatedTicket)

SaveOutputsRequest = _reflection.GeneratedProtocolMessageType(
    "SaveOutputsRequest",
    (_message.Message,),
    {
        "ServiceNumbersSitesMapEntry": _reflection.GeneratedProtocolMessageType(
            "ServiceNumbersSitesMapEntry",
            (_message.Message,),
            {
                "DESCRIPTOR": _SAVEOUTPUTSREQUEST_SERVICENUMBERSSITESMAPENTRY,
                "__module__": "public_input_pb2"
                # @@protoc_insertion_point(class_scope:entrypoint.SaveOutputsRequest.ServiceNumbersSitesMapEntry)
            },
        ),
        "BruinTicketStatusMapEntry": _reflection.GeneratedProtocolMessageType(
            "BruinTicketStatusMapEntry",
            (_message.Message,),
            {
                "DESCRIPTOR": _SAVEOUTPUTSREQUEST_BRUINTICKETSTATUSMAPENTRY,
                "__module__": "public_input_pb2"
                # @@protoc_insertion_point(class_scope:entrypoint.SaveOutputsRequest.BruinTicketStatusMapEntry)
            },
        ),
        "BruinTicketCallTypeMapEntry": _reflection.GeneratedProtocolMessageType(
            "BruinTicketCallTypeMapEntry",
            (_message.Message,),
            {
                "DESCRIPTOR": _SAVEOUTPUTSREQUEST_BRUINTICKETCALLTYPEMAPENTRY,
                "__module__": "public_input_pb2"
                # @@protoc_insertion_point(class_scope:entrypoint.SaveOutputsRequest.BruinTicketCallTypeMapEntry)
            },
        ),
        "BruinTicketCategoryMapEntry": _reflection.GeneratedProtocolMessageType(
            "BruinTicketCategoryMapEntry",
            (_message.Message,),
            {
                "DESCRIPTOR": _SAVEOUTPUTSREQUEST_BRUINTICKETCATEGORYMAPENTRY,
                "__module__": "public_input_pb2"
                # @@protoc_insertion_point(class_scope:entrypoint.SaveOutputsRequest.BruinTicketCategoryMapEntry)
            },
        ),
        "DESCRIPTOR": _SAVEOUTPUTSREQUEST,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.SaveOutputsRequest)
    },
)
_sym_db.RegisterMessage(SaveOutputsRequest)
_sym_db.RegisterMessage(SaveOutputsRequest.ServiceNumbersSitesMapEntry)
_sym_db.RegisterMessage(SaveOutputsRequest.BruinTicketStatusMapEntry)
_sym_db.RegisterMessage(SaveOutputsRequest.BruinTicketCallTypeMapEntry)
_sym_db.RegisterMessage(SaveOutputsRequest.BruinTicketCategoryMapEntry)

SaveOutputsResponse = _reflection.GeneratedProtocolMessageType(
    "SaveOutputsResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _SAVEOUTPUTSRESPONSE,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.SaveOutputsResponse)
    },
)
_sym_db.RegisterMessage(SaveOutputsResponse)

SaveCreatedTicketsFeedbackRequest = _reflection.GeneratedProtocolMessageType(
    "SaveCreatedTicketsFeedbackRequest",
    (_message.Message,),
    {
        "SiteMapEntry": _reflection.GeneratedProtocolMessageType(
            "SiteMapEntry",
            (_message.Message,),
            {
                "DESCRIPTOR": _SAVECREATEDTICKETSFEEDBACKREQUEST_SITEMAPENTRY,
                "__module__": "public_input_pb2"
                # @@protoc_insertion_point(class_scope:entrypoint.SaveCreatedTicketsFeedbackRequest.SiteMapEntry)
            },
        ),
        "DESCRIPTOR": _SAVECREATEDTICKETSFEEDBACKREQUEST,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.SaveCreatedTicketsFeedbackRequest)
    },
)
_sym_db.RegisterMessage(SaveCreatedTicketsFeedbackRequest)
_sym_db.RegisterMessage(SaveCreatedTicketsFeedbackRequest.SiteMapEntry)

SaveCreatedTicketsFeedbackResponse = _reflection.GeneratedProtocolMessageType(
    "SaveCreatedTicketsFeedbackResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _SAVECREATEDTICKETSFEEDBACKRESPONSE,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.SaveCreatedTicketsFeedbackResponse)
    },
)
_sym_db.RegisterMessage(SaveCreatedTicketsFeedbackResponse)

SaveClosedTicketsFeedbackRequest = _reflection.GeneratedProtocolMessageType(
    "SaveClosedTicketsFeedbackRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _SAVECLOSEDTICKETSFEEDBACKREQUEST,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.SaveClosedTicketsFeedbackRequest)
    },
)
_sym_db.RegisterMessage(SaveClosedTicketsFeedbackRequest)

SaveClosedTicketsFeedbackResponse = _reflection.GeneratedProtocolMessageType(
    "SaveClosedTicketsFeedbackResponse",
    (_message.Message,),
    {
        "DESCRIPTOR": _SAVECLOSEDTICKETSFEEDBACKRESPONSE,
        "__module__": "public_input_pb2"
        # @@protoc_insertion_point(class_scope:entrypoint.SaveClosedTicketsFeedbackResponse)
    },
)
_sym_db.RegisterMessage(SaveClosedTicketsFeedbackResponse)

_ENTRYPOINT = DESCRIPTOR.services_by_name["Entrypoint"]
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _SAVEOUTPUTSREQUEST_SERVICENUMBERSSITESMAPENTRY._options = None
    _SAVEOUTPUTSREQUEST_SERVICENUMBERSSITESMAPENTRY._serialized_options = b"8\001"
    _SAVEOUTPUTSREQUEST_BRUINTICKETSTATUSMAPENTRY._options = None
    _SAVEOUTPUTSREQUEST_BRUINTICKETSTATUSMAPENTRY._serialized_options = b"8\001"
    _SAVEOUTPUTSREQUEST_BRUINTICKETCALLTYPEMAPENTRY._options = None
    _SAVEOUTPUTSREQUEST_BRUINTICKETCALLTYPEMAPENTRY._serialized_options = b"8\001"
    _SAVEOUTPUTSREQUEST_BRUINTICKETCATEGORYMAPENTRY._options = None
    _SAVEOUTPUTSREQUEST_BRUINTICKETCATEGORYMAPENTRY._serialized_options = b"8\001"
    _SAVEOUTPUTSREQUEST.fields_by_name["validated_ticket_numbers"]._options = None
    _SAVEOUTPUTSREQUEST.fields_by_name["validated_ticket_numbers"]._serialized_options = b"\030\001"
    _SAVEOUTPUTSREQUEST.fields_by_name["bruin_ticket_status_map"]._options = None
    _SAVEOUTPUTSREQUEST.fields_by_name["bruin_ticket_status_map"]._serialized_options = b"\030\001"
    _SAVEOUTPUTSREQUEST.fields_by_name["bruin_ticket_call_type_map"]._options = None
    _SAVEOUTPUTSREQUEST.fields_by_name["bruin_ticket_call_type_map"]._serialized_options = b"\030\001"
    _SAVEOUTPUTSREQUEST.fields_by_name["bruin_ticket_category_map"]._options = None
    _SAVEOUTPUTSREQUEST.fields_by_name["bruin_ticket_category_map"]._serialized_options = b"\030\001"
    _SAVECREATEDTICKETSFEEDBACKREQUEST_SITEMAPENTRY._options = None
    _SAVECREATEDTICKETSFEEDBACKREQUEST_SITEMAPENTRY._serialized_options = b"8\001"
    _TAG._serialized_start = 34
    _TAG._serialized_end = 74
    _EMAIL._serialized_start = 77
    _EMAIL._serialized_end = 324
    _PREPROCESSEMAILFIELDS._serialized_start = 327
    _PREPROCESSEMAILFIELDS._serialized_end = 458
    _PREPROCESSEMAILOUTPUT._serialized_start = 460
    _PREPROCESSEMAILOUTPUT._serialized_end = 577
    _EXTRACTSERVICENUMBERSOUTPUT._serialized_start = 580
    _EXTRACTSERVICENUMBERSOUTPUT._serialized_end = 772
    _CLASSIFYOUTAGEVSAFFECTINGFIELDS._serialized_start = 775
    _CLASSIFYOUTAGEVSAFFECTINGFIELDS._serialized_end = 1011
    _CLASSIFYOUTAGEVSAFFECTINGOUTPUT._serialized_start = 1014
    _CLASSIFYOUTAGEVSAFFECTINGOUTPUT._serialized_end = 1279
    _PREPAREOUTPUTFIELDS._serialized_start = 1282
    _PREPAREOUTPUTFIELDS._serialized_end = 1629
    _PREDICTIONREQUEST._serialized_start = 1631
    _PREDICTIONREQUEST._serialized_end = 1684
    _OUTPUTFILTERFLAGS._serialized_start = 1687
    _OUTPUTFILTERFLAGS._serialized_end = 1867
    _PREDICTIONRESPONSE._serialized_start = 1870
    _PREDICTIONRESPONSE._serialized_end = 2037
    _TICKET._serialized_start = 2039
    _TICKET._serialized_end = 2137
    _VALIDATEDTICKET._serialized_start = 2139
    _VALIDATEDTICKET._serialized_end = 2252
    _SAVEOUTPUTSREQUEST._serialized_start = 2255
    _SAVEOUTPUTSREQUEST._serialized_end = 3314
    _SAVEOUTPUTSREQUEST_SERVICENUMBERSSITESMAPENTRY._serialized_start = 3066
    _SAVEOUTPUTSREQUEST_SERVICENUMBERSSITESMAPENTRY._serialized_end = 3127
    _SAVEOUTPUTSREQUEST_BRUINTICKETSTATUSMAPENTRY._serialized_start = 3129
    _SAVEOUTPUTSREQUEST_BRUINTICKETSTATUSMAPENTRY._serialized_end = 3188
    _SAVEOUTPUTSREQUEST_BRUINTICKETCALLTYPEMAPENTRY._serialized_start = 3190
    _SAVEOUTPUTSREQUEST_BRUINTICKETCALLTYPEMAPENTRY._serialized_end = 3251
    _SAVEOUTPUTSREQUEST_BRUINTICKETCATEGORYMAPENTRY._serialized_start = 3253
    _SAVEOUTPUTSREQUEST_BRUINTICKETCATEGORYMAPENTRY._serialized_end = 3314
    _SAVEOUTPUTSRESPONSE._serialized_start = 3316
    _SAVEOUTPUTSRESPONSE._serialized_end = 3354
    _SAVECREATEDTICKETSFEEDBACKREQUEST._serialized_start = 3357
    _SAVECREATEDTICKETSFEEDBACKREQUEST._serialized_end = 3643
    _SAVECREATEDTICKETSFEEDBACKREQUEST_SITEMAPENTRY._serialized_start = 3597
    _SAVECREATEDTICKETSFEEDBACKREQUEST_SITEMAPENTRY._serialized_end = 3643
    _SAVECREATEDTICKETSFEEDBACKRESPONSE._serialized_start = 3645
    _SAVECREATEDTICKETSFEEDBACKRESPONSE._serialized_end = 3698
    _SAVECLOSEDTICKETSFEEDBACKREQUEST._serialized_start = 3700
    _SAVECLOSEDTICKETSFEEDBACKREQUEST._serialized_end = 3822
    _SAVECLOSEDTICKETSFEEDBACKRESPONSE._serialized_start = 3824
    _SAVECLOSEDTICKETSFEEDBACKRESPONSE._serialized_end = 3876
    _ENTRYPOINT._serialized_start = 3879
    _ENTRYPOINT._serialized_end = 4306
# @@protoc_insertion_point(module_scope)
