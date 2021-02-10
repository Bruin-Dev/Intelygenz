# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: public_input.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor.FileDescriptor(
    name='public_input.proto',
    package='entrypoint',
    syntax='proto3',
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
    serialized_pb=b'\n\x12public_input.proto\x12\nentrypoint\"\xf4\x03\n\tTicketRow\x12\r\n\x05\x61sset\x18\x01 \x01(\t\x12\x0f\n\x07product\x18\x02 \x01(\t\x12\x14\n\x0c\x65ntered_date\x18\x03 \x01(\t\x12\r\n\x05notes\x18\x04 \x01(\t\x12\x13\n\x0btask_result\x18\x05 \x01(\t\x12\x13\n\x0b\x63lient_name\x18\x06 \x01(\t\x12\x0c\n\x04\x63ity\x18\x07 \x01(\t\x12\r\n\x05state\x18\x08 \x01(\t\x12\x16\n\x0e\x65ntered_date_n\x18\t \x01(\t\x12\x17\n\x0fnote_entered_by\x18\n \x01(\t\x12\x1b\n\x13ticket_entered_date\x18\x0b \x01(\t\x12\x16\n\x0e\x63\x61ll_ticket_id\x18\x0c \x01(\x03\x12$\n\x1cinitial_note_ticket_creation\x18\r \x01(\t\x12\x11\n\tdetail_id\x18\x0e \x01(\x03\x12\x10\n\x08\x61\x64\x64ress1\x18\x0f \x01(\t\x12\x10\n\x08\x61\x64\x64ress2\x18\x10 \x01(\t\x12\x0b\n\x03zip\x18\x11 \x01(\t\x12\x11\n\tsite_name\x18\x12 \x01(\t\x12\x11\n\tnote_type\x18\x13 \x01(\t\x12\x19\n\x11note_entered_date\x18\x14 \x01(\t\x12\x18\n\x10task_assigned_to\x18\x15 \x01(\t\x12\x0c\n\x04task\x18\x16 \x01(\t\x12\x0b\n\x03sla\x18\x17 \x01(\x05\x12\x15\n\rticket_status\x18\x18 \x01(\t\"/\n\nTaskResult\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0bprobability\x18\x02 \x01(\x02\"&\n\x05\x45rror\x12\x0c\n\x04\x63ode\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"p\n\x0f\x41ssetPrediction\x12\r\n\x05\x61sset\x18\x01 \x01(\t\x12,\n\x0ctask_results\x18\x02 \x03(\x0b\x32\x16.entrypoint.TaskResult\x12 \n\x05\x65rror\x18\x03 \x01(\x0b\x32\x11.entrypoint.Error\"m\n\x11PredictionRequest\x12\x11\n\tticket_id\x18\x01 \x01(\x03\x12*\n\x0bticket_rows\x18\x02 \x03(\x0b\x32\x15.entrypoint.TicketRow\x12\x19\n\x11\x61ssets_to_predict\x18\x03 \x03(\t\"\x81\x01\n\x12PredictionResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x11\n\tticket_id\x18\x03 \x01(\x03\x12\x36\n\x11\x61sset_predictions\x18\x04 \x03(\x0b\x32\x1b.entrypoint.AssetPrediction\"S\n\x12SaveMetricsRequest\x12\x11\n\tticket_id\x18\x01 \x01(\x03\x12*\n\x0bticket_rows\x18\x02 \x03(\x0b\x32\x15.entrypoint.TicketRow\"&\n\x13SaveMetricsResponse\x12\x0f\n\x07message\x18\x01 \x01(\t2\xad\x01\n\nEntrypoint\x12M\n\nPrediction\x12\x1d.entrypoint.PredictionRequest\x1a\x1e.entrypoint.PredictionResponse\"\x00\x12P\n\x0bSaveMetrics\x12\x1e.entrypoint.SaveMetricsRequest\x1a\x1f.entrypoint.SaveMetricsResponse\"\x00\x62\x06proto3'  # noqa
)

_TICKETROW = _descriptor.Descriptor(
    name='TicketRow',
    full_name='entrypoint.TicketRow',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name='asset', full_name='entrypoint.TicketRow.asset', index=0,
            number=1, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='product', full_name='entrypoint.TicketRow.product', index=1,
            number=2, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='entered_date', full_name='entrypoint.TicketRow.entered_date', index=2,
            number=3, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='notes', full_name='entrypoint.TicketRow.notes', index=3,
            number=4, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='task_result', full_name='entrypoint.TicketRow.task_result', index=4,
            number=5, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='client_name', full_name='entrypoint.TicketRow.client_name', index=5,
            number=6, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='city', full_name='entrypoint.TicketRow.city', index=6,
            number=7, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='state', full_name='entrypoint.TicketRow.state', index=7,
            number=8, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='entered_date_n', full_name='entrypoint.TicketRow.entered_date_n', index=8,
            number=9, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='note_entered_by', full_name='entrypoint.TicketRow.note_entered_by', index=9,
            number=10, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='ticket_entered_date', full_name='entrypoint.TicketRow.ticket_entered_date', index=10,
            number=11, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='call_ticket_id', full_name='entrypoint.TicketRow.call_ticket_id', index=11,
            number=12, type=3, cpp_type=2, label=1,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='initial_note_ticket_creation', full_name='entrypoint.TicketRow.initial_note_ticket_creation',
            index=12,
            number=13, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='detail_id', full_name='entrypoint.TicketRow.detail_id', index=13,
            number=14, type=3, cpp_type=2, label=1,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='address1', full_name='entrypoint.TicketRow.address1', index=14,
            number=15, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='address2', full_name='entrypoint.TicketRow.address2', index=15,
            number=16, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='zip', full_name='entrypoint.TicketRow.zip', index=16,
            number=17, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='site_name', full_name='entrypoint.TicketRow.site_name', index=17,
            number=18, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='note_type', full_name='entrypoint.TicketRow.note_type', index=18,
            number=19, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='note_entered_date', full_name='entrypoint.TicketRow.note_entered_date', index=19,
            number=20, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='task_assigned_to', full_name='entrypoint.TicketRow.task_assigned_to', index=20,
            number=21, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='task', full_name='entrypoint.TicketRow.task', index=21,
            number=22, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='sla', full_name='entrypoint.TicketRow.sla', index=22,
            number=23, type=5, cpp_type=1, label=1,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='ticket_status', full_name='entrypoint.TicketRow.ticket_status', index=23,
            number=24, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=35,
    serialized_end=535,
)

_TASKRESULT = _descriptor.Descriptor(
    name='TaskResult',
    full_name='entrypoint.TaskResult',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name='name', full_name='entrypoint.TaskResult.name', index=0,
            number=1, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='probability', full_name='entrypoint.TaskResult.probability', index=1,
            number=2, type=2, cpp_type=6, label=1,
            has_default_value=False, default_value=float(0),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=537,
    serialized_end=584,
)

_ERROR = _descriptor.Descriptor(
    name='Error',
    full_name='entrypoint.Error',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name='code', full_name='entrypoint.Error.code', index=0,
            number=1, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='message', full_name='entrypoint.Error.message', index=1,
            number=2, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=586,
    serialized_end=624,
)

_ASSETPREDICTION = _descriptor.Descriptor(
    name='AssetPrediction',
    full_name='entrypoint.AssetPrediction',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name='asset', full_name='entrypoint.AssetPrediction.asset', index=0,
            number=1, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='task_results', full_name='entrypoint.AssetPrediction.task_results', index=1,
            number=2, type=11, cpp_type=10, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='error', full_name='entrypoint.AssetPrediction.error', index=2,
            number=3, type=11, cpp_type=10, label=1,
            has_default_value=False, default_value=None,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=626,
    serialized_end=738,
)

_PREDICTIONREQUEST = _descriptor.Descriptor(
    name='PredictionRequest',
    full_name='entrypoint.PredictionRequest',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name='ticket_id', full_name='entrypoint.PredictionRequest.ticket_id', index=0,
            number=1, type=3, cpp_type=2, label=1,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='ticket_rows', full_name='entrypoint.PredictionRequest.ticket_rows', index=1,
            number=2, type=11, cpp_type=10, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='assets_to_predict', full_name='entrypoint.PredictionRequest.assets_to_predict', index=2,
            number=3, type=9, cpp_type=9, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=740,
    serialized_end=849,
)

_PREDICTIONRESPONSE = _descriptor.Descriptor(
    name='PredictionResponse',
    full_name='entrypoint.PredictionResponse',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name='success', full_name='entrypoint.PredictionResponse.success', index=0,
            number=1, type=8, cpp_type=7, label=1,
            has_default_value=False, default_value=False,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='message', full_name='entrypoint.PredictionResponse.message', index=1,
            number=2, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='ticket_id', full_name='entrypoint.PredictionResponse.ticket_id', index=2,
            number=3, type=3, cpp_type=2, label=1,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='asset_predictions', full_name='entrypoint.PredictionResponse.asset_predictions', index=3,
            number=4, type=11, cpp_type=10, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=852,
    serialized_end=981,
)

_SAVEMETRICSREQUEST = _descriptor.Descriptor(
    name='SaveMetricsRequest',
    full_name='entrypoint.SaveMetricsRequest',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name='ticket_id', full_name='entrypoint.SaveMetricsRequest.ticket_id', index=0,
            number=1, type=3, cpp_type=2, label=1,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
        _descriptor.FieldDescriptor(
            name='ticket_rows', full_name='entrypoint.SaveMetricsRequest.ticket_rows', index=1,
            number=2, type=11, cpp_type=10, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=983,
    serialized_end=1066,
)

_SAVEMETRICSRESPONSE = _descriptor.Descriptor(
    name='SaveMetricsResponse',
    full_name='entrypoint.SaveMetricsResponse',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name='message', full_name='entrypoint.SaveMetricsResponse.message', index=0,
            number=1, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=b"".decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR, create_key=_descriptor._internal_create_key),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto3',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=1068,
    serialized_end=1106,
)

_ASSETPREDICTION.fields_by_name['task_results'].message_type = _TASKRESULT
_ASSETPREDICTION.fields_by_name['error'].message_type = _ERROR
_PREDICTIONREQUEST.fields_by_name['ticket_rows'].message_type = _TICKETROW
_PREDICTIONRESPONSE.fields_by_name['asset_predictions'].message_type = _ASSETPREDICTION
_SAVEMETRICSREQUEST.fields_by_name['ticket_rows'].message_type = _TICKETROW
DESCRIPTOR.message_types_by_name['TicketRow'] = _TICKETROW
DESCRIPTOR.message_types_by_name['TaskResult'] = _TASKRESULT
DESCRIPTOR.message_types_by_name['Error'] = _ERROR
DESCRIPTOR.message_types_by_name['AssetPrediction'] = _ASSETPREDICTION
DESCRIPTOR.message_types_by_name['PredictionRequest'] = _PREDICTIONREQUEST
DESCRIPTOR.message_types_by_name['PredictionResponse'] = _PREDICTIONRESPONSE
DESCRIPTOR.message_types_by_name['SaveMetricsRequest'] = _SAVEMETRICSREQUEST
DESCRIPTOR.message_types_by_name['SaveMetricsResponse'] = _SAVEMETRICSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TicketRow = _reflection.GeneratedProtocolMessageType('TicketRow', (_message.Message,), {
    'DESCRIPTOR': _TICKETROW,
    '__module__': 'public_input_pb2'
    # @@protoc_insertion_point(class_scope:entrypoint.TicketRow)
})
_sym_db.RegisterMessage(TicketRow)

TaskResult = _reflection.GeneratedProtocolMessageType('TaskResult', (_message.Message,), {
    'DESCRIPTOR': _TASKRESULT,
    '__module__': 'public_input_pb2'
    # @@protoc_insertion_point(class_scope:entrypoint.TaskResult)
})
_sym_db.RegisterMessage(TaskResult)

Error = _reflection.GeneratedProtocolMessageType('Error', (_message.Message,), {
    'DESCRIPTOR': _ERROR,
    '__module__': 'public_input_pb2'
    # @@protoc_insertion_point(class_scope:entrypoint.Error)
})
_sym_db.RegisterMessage(Error)

AssetPrediction = _reflection.GeneratedProtocolMessageType('AssetPrediction', (_message.Message,), {
    'DESCRIPTOR': _ASSETPREDICTION,
    '__module__': 'public_input_pb2'
    # @@protoc_insertion_point(class_scope:entrypoint.AssetPrediction)
})
_sym_db.RegisterMessage(AssetPrediction)

PredictionRequest = _reflection.GeneratedProtocolMessageType('PredictionRequest', (_message.Message,), {
    'DESCRIPTOR': _PREDICTIONREQUEST,
    '__module__': 'public_input_pb2'
    # @@protoc_insertion_point(class_scope:entrypoint.PredictionRequest)
})
_sym_db.RegisterMessage(PredictionRequest)

PredictionResponse = _reflection.GeneratedProtocolMessageType('PredictionResponse', (_message.Message,), {
    'DESCRIPTOR': _PREDICTIONRESPONSE,
    '__module__': 'public_input_pb2'
    # @@protoc_insertion_point(class_scope:entrypoint.PredictionResponse)
})
_sym_db.RegisterMessage(PredictionResponse)

SaveMetricsRequest = _reflection.GeneratedProtocolMessageType('SaveMetricsRequest', (_message.Message,), {
    'DESCRIPTOR': _SAVEMETRICSREQUEST,
    '__module__': 'public_input_pb2'
    # @@protoc_insertion_point(class_scope:entrypoint.SaveMetricsRequest)
})
_sym_db.RegisterMessage(SaveMetricsRequest)

SaveMetricsResponse = _reflection.GeneratedProtocolMessageType('SaveMetricsResponse', (_message.Message,), {
    'DESCRIPTOR': _SAVEMETRICSRESPONSE,
    '__module__': 'public_input_pb2'
    # @@protoc_insertion_point(class_scope:entrypoint.SaveMetricsResponse)
})
_sym_db.RegisterMessage(SaveMetricsResponse)

_ENTRYPOINT = _descriptor.ServiceDescriptor(
    name='Entrypoint',
    full_name='entrypoint.Entrypoint',
    file=DESCRIPTOR,
    index=0,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
    serialized_start=1109,
    serialized_end=1282,
    methods=[
        _descriptor.MethodDescriptor(
            name='Prediction',
            full_name='entrypoint.Entrypoint.Prediction',
            index=0,
            containing_service=None,
            input_type=_PREDICTIONREQUEST,
            output_type=_PREDICTIONRESPONSE,
            serialized_options=None,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.MethodDescriptor(
            name='SaveMetrics',
            full_name='entrypoint.Entrypoint.SaveMetrics',
            index=1,
            containing_service=None,
            input_type=_SAVEMETRICSREQUEST,
            output_type=_SAVEMETRICSRESPONSE,
            serialized_options=None,
            create_key=_descriptor._internal_create_key,
        ),
    ])
_sym_db.RegisterServiceDescriptor(_ENTRYPOINT)

DESCRIPTOR.services_by_name['Entrypoint'] = _ENTRYPOINT

# @@protoc_insertion_point(module_scope)
