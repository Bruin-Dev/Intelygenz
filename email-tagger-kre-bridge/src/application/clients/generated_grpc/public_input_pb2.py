# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: public_input.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
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
  serialized_pb=_b('\n\x12public_input.proto\x12\nentrypoint\"\x87\x01\n\x05\x45mail\x12\x10\n\x08\x65mail_id\x18\x01 \x01(\t\x12\x0c\n\x04\x64\x61te\x18\x02 \x01(\t\x12\x0f\n\x07subject\x18\x03 \x01(\t\x12\x0c\n\x04\x62ody\x18\x04 \x01(\t\x12\x11\n\tparent_id\x18\x05 \x01(\t\x12\x19\n\x11previous_email_id\x18\x06 \x01(\t\x12\x11\n\tclient_id\x18\x07 \x01(\t\"F\n\x11PredictionRequest\x12 \n\x05\x65mail\x18\x01 \x01(\x0b\x32\x11.entrypoint.Email\x12\x0f\n\x07tag_ids\x18\x02 \x03(\x03\"\xba\x01\n\x12PredictionResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x10\n\x08\x65mail_id\x18\x03 \x01(\t\x12=\n\nprediction\x18\x04 \x03(\x0b\x32).entrypoint.PredictionResponse.Prediction\x1a\x31\n\nPrediction\x12\x0e\n\x06tag_id\x18\x01 \x01(\x03\x12\x13\n\x0bprobability\x18\x02 \x01(\x02\"\xeb\x01\n\x12SaveMetricsRequest\x12\x35\n\x0eoriginal_email\x18\x01 \x01(\x0b\x32\x1d.entrypoint.PredictionRequest\x12\x35\n\x06ticket\x18\x02 \x01(\x0b\x32%.entrypoint.SaveMetricsRequest.Ticket\x1ag\n\x06Ticket\x12\x11\n\tticket_id\x18\x01 \x01(\x03\x12\x11\n\tcall_type\x18\x02 \x01(\t\x12\x10\n\x08\x63\x61tegory\x18\x03 \x01(\t\x12\x15\n\rcreation_date\x18\x04 \x01(\t\x12\x0e\n\x06status\x18\x05 \x01(\t\"&\n\x13SaveMetricsResponse\x12\x0f\n\x07message\x18\x01 \x01(\t2\xb0\x01\n\nEntrypoint\x12P\n\rGetPrediction\x12\x1d.entrypoint.PredictionRequest\x1a\x1e.entrypoint.PredictionResponse\"\x00\x12P\n\x0bSaveMetrics\x12\x1e.entrypoint.SaveMetricsRequest\x1a\x1f.entrypoint.SaveMetricsResponse\"\x00\x62\x06proto3')
)




_EMAIL = _descriptor.Descriptor(
  name='Email',
  full_name='entrypoint.Email',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='email_id', full_name='entrypoint.Email.email_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='date', full_name='entrypoint.Email.date', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='subject', full_name='entrypoint.Email.subject', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='body', full_name='entrypoint.Email.body', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='parent_id', full_name='entrypoint.Email.parent_id', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='previous_email_id', full_name='entrypoint.Email.previous_email_id', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='client_id', full_name='entrypoint.Email.client_id', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
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
  serialized_end=170,
)


_PREDICTIONREQUEST = _descriptor.Descriptor(
  name='PredictionRequest',
  full_name='entrypoint.PredictionRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='email', full_name='entrypoint.PredictionRequest.email', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='tag_ids', full_name='entrypoint.PredictionRequest.tag_ids', index=1,
      number=2, type=3, cpp_type=2, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
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
  serialized_start=172,
  serialized_end=242,
)


_PREDICTIONRESPONSE_PREDICTION = _descriptor.Descriptor(
  name='Prediction',
  full_name='entrypoint.PredictionResponse.Prediction',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='tag_id', full_name='entrypoint.PredictionResponse.Prediction.tag_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='probability', full_name='entrypoint.PredictionResponse.Prediction.probability', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
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
  serialized_start=382,
  serialized_end=431,
)

_PREDICTIONRESPONSE = _descriptor.Descriptor(
  name='PredictionResponse',
  full_name='entrypoint.PredictionResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='success', full_name='entrypoint.PredictionResponse.success', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='message', full_name='entrypoint.PredictionResponse.message', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='email_id', full_name='entrypoint.PredictionResponse.email_id', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='prediction', full_name='entrypoint.PredictionResponse.prediction', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_PREDICTIONRESPONSE_PREDICTION, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=245,
  serialized_end=431,
)


_SAVEMETRICSREQUEST_TICKET = _descriptor.Descriptor(
  name='Ticket',
  full_name='entrypoint.SaveMetricsRequest.Ticket',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ticket_id', full_name='entrypoint.SaveMetricsRequest.Ticket.ticket_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='call_type', full_name='entrypoint.SaveMetricsRequest.Ticket.call_type', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='category', full_name='entrypoint.SaveMetricsRequest.Ticket.category', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='creation_date', full_name='entrypoint.SaveMetricsRequest.Ticket.creation_date', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='status', full_name='entrypoint.SaveMetricsRequest.Ticket.status', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
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
  serialized_start=566,
  serialized_end=669,
)

_SAVEMETRICSREQUEST = _descriptor.Descriptor(
  name='SaveMetricsRequest',
  full_name='entrypoint.SaveMetricsRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='original_email', full_name='entrypoint.SaveMetricsRequest.original_email', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ticket', full_name='entrypoint.SaveMetricsRequest.ticket', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_SAVEMETRICSREQUEST_TICKET, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=434,
  serialized_end=669,
)


_SAVEMETRICSRESPONSE = _descriptor.Descriptor(
  name='SaveMetricsResponse',
  full_name='entrypoint.SaveMetricsResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message', full_name='entrypoint.SaveMetricsResponse.message', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
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
  serialized_start=671,
  serialized_end=709,
)

_PREDICTIONREQUEST.fields_by_name['email'].message_type = _EMAIL
_PREDICTIONRESPONSE_PREDICTION.containing_type = _PREDICTIONRESPONSE
_PREDICTIONRESPONSE.fields_by_name['prediction'].message_type = _PREDICTIONRESPONSE_PREDICTION
_SAVEMETRICSREQUEST_TICKET.containing_type = _SAVEMETRICSREQUEST
_SAVEMETRICSREQUEST.fields_by_name['original_email'].message_type = _PREDICTIONREQUEST
_SAVEMETRICSREQUEST.fields_by_name['ticket'].message_type = _SAVEMETRICSREQUEST_TICKET
DESCRIPTOR.message_types_by_name['Email'] = _EMAIL
DESCRIPTOR.message_types_by_name['PredictionRequest'] = _PREDICTIONREQUEST
DESCRIPTOR.message_types_by_name['PredictionResponse'] = _PREDICTIONRESPONSE
DESCRIPTOR.message_types_by_name['SaveMetricsRequest'] = _SAVEMETRICSREQUEST
DESCRIPTOR.message_types_by_name['SaveMetricsResponse'] = _SAVEMETRICSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Email = _reflection.GeneratedProtocolMessageType('Email', (_message.Message,), dict(
  DESCRIPTOR = _EMAIL,
  __module__ = 'public_input_pb2'
  # @@protoc_insertion_point(class_scope:entrypoint.Email)
  ))
_sym_db.RegisterMessage(Email)

PredictionRequest = _reflection.GeneratedProtocolMessageType('PredictionRequest', (_message.Message,), dict(
  DESCRIPTOR = _PREDICTIONREQUEST,
  __module__ = 'public_input_pb2'
  # @@protoc_insertion_point(class_scope:entrypoint.PredictionRequest)
  ))
_sym_db.RegisterMessage(PredictionRequest)

PredictionResponse = _reflection.GeneratedProtocolMessageType('PredictionResponse', (_message.Message,), dict(

  Prediction = _reflection.GeneratedProtocolMessageType('Prediction', (_message.Message,), dict(
    DESCRIPTOR = _PREDICTIONRESPONSE_PREDICTION,
    __module__ = 'public_input_pb2'
    # @@protoc_insertion_point(class_scope:entrypoint.PredictionResponse.Prediction)
    ))
  ,
  DESCRIPTOR = _PREDICTIONRESPONSE,
  __module__ = 'public_input_pb2'
  # @@protoc_insertion_point(class_scope:entrypoint.PredictionResponse)
  ))
_sym_db.RegisterMessage(PredictionResponse)
_sym_db.RegisterMessage(PredictionResponse.Prediction)

SaveMetricsRequest = _reflection.GeneratedProtocolMessageType('SaveMetricsRequest', (_message.Message,), dict(

  Ticket = _reflection.GeneratedProtocolMessageType('Ticket', (_message.Message,), dict(
    DESCRIPTOR = _SAVEMETRICSREQUEST_TICKET,
    __module__ = 'public_input_pb2'
    # @@protoc_insertion_point(class_scope:entrypoint.SaveMetricsRequest.Ticket)
    ))
  ,
  DESCRIPTOR = _SAVEMETRICSREQUEST,
  __module__ = 'public_input_pb2'
  # @@protoc_insertion_point(class_scope:entrypoint.SaveMetricsRequest)
  ))
_sym_db.RegisterMessage(SaveMetricsRequest)
_sym_db.RegisterMessage(SaveMetricsRequest.Ticket)

SaveMetricsResponse = _reflection.GeneratedProtocolMessageType('SaveMetricsResponse', (_message.Message,), dict(
  DESCRIPTOR = _SAVEMETRICSRESPONSE,
  __module__ = 'public_input_pb2'
  # @@protoc_insertion_point(class_scope:entrypoint.SaveMetricsResponse)
  ))
_sym_db.RegisterMessage(SaveMetricsResponse)



_ENTRYPOINT = _descriptor.ServiceDescriptor(
  name='Entrypoint',
  full_name='entrypoint.Entrypoint',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=712,
  serialized_end=888,
  methods=[
  _descriptor.MethodDescriptor(
    name='GetPrediction',
    full_name='entrypoint.Entrypoint.GetPrediction',
    index=0,
    containing_service=None,
    input_type=_PREDICTIONREQUEST,
    output_type=_PREDICTIONRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='SaveMetrics',
    full_name='entrypoint.Entrypoint.SaveMetrics',
    index=1,
    containing_service=None,
    input_type=_SAVEMETRICSREQUEST,
    output_type=_SAVEMETRICSRESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_ENTRYPOINT)

DESCRIPTOR.services_by_name['Entrypoint'] = _ENTRYPOINT

# @@protoc_insertion_point(module_scope)