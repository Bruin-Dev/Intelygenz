# Bruin Bridge Event Logging

# Description

The mission of this service is to act as a proxy to the Bruin API. It accepts requests from other services and yields
the requested data back to those services so they can make the appropriate business decision.

## Process Workflows
![[](../../images/11-bruin-bridge.png)](../../images/11-bruin-bridge.jpg)

## List of Decisions made by the Bruin Bridge
### Subject: bruin.ticket.request (aims at endpoint [GET /api/Ticket](https://api.bruin.com/index.html#/Ticket/get_api_Ticket))
|     | Condition                                          | Decision                     | Decision                         |
|-----|----------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request    | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Ticket  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.ticket.basic.request (aims at endpoint [GET /api/Ticket/basic](https://api.bruin.com/index.html#/Ticket/get_api_Ticket_basic))
|     | Condition                                               | Decision                     | Decision                         |
|-----|---------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request         | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Ticket/basic | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.get.site (aims at endpoint [GET /api/Site](https://api.bruin.com/index.html#/Site/get_api_Site))
|     | Condition                                       | Decision                        | Decision                            |
|-----|-------------------------------------------------|---------------------------------|-------------------------------------|
| 1   | Check for shape and content of incoming request | Request has valid format        | Request has invalid format          |
| 2   | Check for status of response from GET /api/Site | HTTP response has status 200    | HTTP response has NOT status 200    |
| 3   | Check for existence of site's data              | Site info was found for filters | Site info was NOT found for filters |

### Subject: bruin.change.ticket.severity (aims at endpoint [PUT /api/Ticket/{ticketId}/severity](https://api.bruin.com/index.html#/Ticket/put_api_Ticket__ticketId__severity))
|     | Condition                                                             | Decision                     | Decision                         |
|-----|-----------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                       | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from PUT /api/Ticket/{ticketId}/severity | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.single.basic.request (aims at endpoint [GET /api/Ticket/basic](https://api.bruin.com/index.html#/Ticket/get_api_Ticket_basic))
|     | Condition                                                | Decision                     | Decision                         |
|-----|----------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request          | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Ticket/basic  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.ticket.detail.request (aims at endpoint [GET /api/Ticket/{ticket_id}/details](https://api.bruin.com/index.html#/Ticket/get_api_Ticket__ticketId__details))
|     | Condition                                                              | Decision                     | Decision                         |
|-----|------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                        | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Ticket/{ticket_id}/details  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.ticket.note.append.request (aims at endpoint [POST /api/Ticket/{ticket_id}/notes](https://api.bruin.com/index.html#/Ticket/post_api_Ticket__ticketId__notes))
|     | Condition                                                             | Decision                     | Decision                         |
|-----|-----------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                       | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /api/Ticket/{ticket_id}/notes  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.ticket.multiple.note.append.request (aims at endpoint [POST /api/Ticket/{ticket_id}/notes/advanced](https://api.bruin.com/index.html#/Ticket/post_api_Ticket__ticketId__notes_advanced))
|     | Condition                                                                      | Decision                     | Decision                         |
|-----|--------------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                                | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /api/Ticket/{ticket_id}/notes/advanced  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.ticket.creation.request (aims at endpoint [POST /api/Ticket/](https://api.bruin.com/index.html#/Ticket/post_api_Ticket))
|     | Condition                                            | Decision                     | Decision                         |
|-----|------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request      | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /api/Ticket/  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.ticket.status.open (aims at endpoint [PUT /api/Ticket/{ticket_id}/details/{detail_id}/status](https://api.bruin.com/index.html#/Ticket/put_api_Ticket__ticketId__details__detailId__status))
|     | Condition                                                                                 | Decision                     | Decision                         |
|-----|-------------------------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                                           | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from PUT /api/Ticket/{ticket_id}/details/{detail_id}/status  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.ticket.status.resolve (aims at endpoint [PUT /api/Ticket/{ticket_id}/details/{detail_id}/status](https://api.bruin.com/index.html#/Ticket/put_api_Ticket__ticketId__details__detailId__status))
|     | Condition                                                                                 | Decision                     | Decision                         |
|-----|-------------------------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                                           | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from PUT /api/Ticket/{ticket_id}/details/{detail_id}/status  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.inventory.attributes.serial (aims at endpoint [GET /api/Inventory/Attribute](https://api.bruin.com/index.html#/Inventory/get_api_Inventory_Attribute))
|     | Condition                                                      | Decision                     | Decision                         |
|-----|----------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Inventory/Attribute | HTTP response has status 200 | HTTP response has NOT status 200 |
| 3   | Check for existence of serial number in attributes response    | Serial number is found       | Serial number is NOT found       |

### Subject: bruin.inventory.attributes.serial (aims at endpoint [GET /api/Inventory/Attribute](https://api.bruin.com/index.html#/Inventory/get_api_Inventory_Attribute))
|     | Condition                                                      | Decision                     | Decision                         |
|-----|----------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Inventory/Attribute | HTTP response has status 200 | HTTP response has NOT status 200 |
| 3   | Check for existence of serial number in attributes response    | Serial number is found       | Serial number is NOT found       |

### Subject: bruin.inventory.management.status (aims at endpoint [GET /api/Inventory/Attribute](https://api.bruin.com/index.html#/Inventory/get_api_Inventory_Attribute))
|     | Condition                                                       | Decision                        | Decision                         |
|-----|-----------------------------------------------------------------|---------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                 | Request has valid format        | Request has invalid format       |
| 2   | Check for status of response from PUT /api/Inventory/Attribute  | HTTP response has status 200    | HTTP response has NOT status 200 |
| 3   | Check for existence of Management Status in attributes response | Management Status is found      | Management Status  is NOT found  |

### Subject: bruin.ticket.creation.outage.request (aims at endpoint [POST /api/Ticket/repair](https://api.bruin.com/index.html#/Ticket/post_api_Ticket_repair))
|     | Condition                                                       | Decision                        | Decision                         |
|-----|-----------------------------------------------------------------|---------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                 | Request has valid format        | Request has invalid format       |
| 2   | Check for status of response from POST /api/Ticket/repair       | HTTP response has status 200    | HTTP response has NOT status 200 |

|     | Condition                                                      | Decision                               | Decision            | Decision         | Decision          | Decision          |
|-----|----------------------------------------------------------------|----------------------------------------|---------------------|------------------|-------------------|-------------------|
| 3   | Check errorCode field of a HTTP response that has a status 200 | errorCode is not 409, 471, 472, or 473 | errorCode is 409    | errorCode is 471 | errorCode is 472  | errorCode is 473  |

### Subject: bruin.customer.get.info (aims at endpoint [GET /api/Inventory](https://api.bruin.com/index.html#/Inventory/get_api_Inventory))
|     | Condition                                             | Decision                     | Decision                         |
|-----|-------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request       | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Inventory  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.customer.get.info_by_did (aims at endpoint [GET /api/Inventory/phoneNumber/Lines](https://api.bruin.com/index.html#/Inventory/get_api_Inventory_phoneNumber_Lines))
|     | Condition                                                               | Decision                     | Decision                         |
|-----|-------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                         | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Inventory/phoneNumber/Lines  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.ticket.change.work (aims at endpoint [GET /api/Ticket/{ticket_id}/nextresult](https://api.bruin.com/index.html#/Ticket/get_api_Ticket__ticketId__nextresult) and [PUT /api/Ticket/{ticket_id}/details/work](https://api.bruin.com/index.html#/Ticket/put_api_Ticket__ticketId__details_work))
|     | Condition                                                                                          | Decision                     | Decision                         |
|-----|----------------------------------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                                                    | Request has valid format     | Request has invalid format       |

|     | Condition                                                                                          | Decision           | Decision                                 | Decision                       | Decision                                           | Decision                         |
|-----|----------------------------------------------------------------------------------------------------|--------------------|------------------------------------------|--------------------------------|----------------------------------------------------|----------------------------------|
| 2   | Check for status and work queues' existence of response from GET api/Ticket/{ticket_id}/nextresult | Work queue exists  | Ticket Id is already in that work queue  | No possible work queue exists  | No possible work queue exists with work queue name | HTTP response has NOT status 200 |

|     | Condition                                                               | Decision                         | Decision                          |
|-----|-------------------------------------------------------------------------|----------------------------------|-----------------------------------|
| 3   |  Check for status of response from /api/Ticket/{ticket_id}/details/work | HTTP response has status 200     | HTTP response has NOT status 200  |

### Subject: bruin.ticket.get.task.history (aims at endpoint [GET /api/Ticket/AITicketData](https://api.bruin.com/index.html#/Ticket/get_api_Ticket_AITicketData))
|     | Condition                                                       | Decision                     | Decision                         |
|-----|-----------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                 | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Ticket/AITicketData  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.ticket.detail.get.next.result (aims at endpoint [GET /api/Ticket/{ticket_id}/nextresult](https://api.bruin.com/index.html#/Ticket/get_api_Ticket__ticketId__nextresult))
|     | Condition                                                                 | Decision                     | Decision                         |
|-----|---------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                           | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Ticket/{ticket_id}/nextresult  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.ticket.unpause (aims at endpoint [POST /api/Ticket/{ticket_id}/detail/unpause](https://api.bruin.com/index.html#/Ticket/post_api_Ticket__ticketId__detail_unpause))
|     | Condition                                                                     | Decision                     | Decision                         |
|-----|-------------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                               | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /api/Ticket/{ticket_id}/detail/unpause | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.email.tag.request (aims at endpoint [POST api/Email/{email_id}/tag/{tag_id}](https://api.bruin.com/index.html#/Email/post_api_Email__messageId__tag__tagTypeId_))
|     | Condition                                                                 | Decision                     | Decision                         |
|-----|---------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                           | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST api/Email/{email_id}/tag/{tag_id}  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.get.circuit.id (aims at endpoint [GET /api/Inventory/circuit](https://api.bruin.com/index.html#/Inventory/get_api_Inventory_circuit))
|     | Condition                                                     | Decision                     | Decision                         |
|-----|---------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request               | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Inventory/circuit  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.get.circuit.id (aims at endpoint [GET /api/Inventory/circuit](https://api.bruin.com/index.html#/Inventory/get_api_Inventory_circuit))
|     | Condition                                                     | Decision                     | Decision                         |
|-----|---------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request               | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Inventory/circuit  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.mark.email.done (aims at endpoint [POST /api/Email/status](https://api.bruin.com/index.html#/Email/post_api_Email_status))
|     | Condition                                                | Decision                     | Decision                         |
|-----|----------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request          | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /api/Email/status | HTTP response has status 200 | HTTP response has NOT status 200 |
| 3   | Check for existence of success field                     | success field exists         | success field does NOT exists    |

### Subject: bruin.link.ticket.email (aims at endpoint [POST /api/Email/{email_id}/link/ticket/{ticket_id}](https://api.bruin.com/index.html#/Email/post_api_Email__emailId__link_ticket__ticketId_))
|     | Condition                                                                             | Decision                     | Decision                         |
|-----|---------------------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                                       | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /api/Email/{email_id}/link/ticket/{ticket_id}  | HTTP response has status 200 | HTTP response has NOT status 200 |
| 3   | Check for existence of success field                                                  | success field exists         | success field does NOT exists    |

### Subject: bruin.notification.email.milestone (aims at endpoint [POST /api/Notification/email/milestone](https://api.bruin.com/index.html#/Notification/post_api_Notification_email_milestone))
|     | Condition                                                                 | Decision                     | Decision                         |
|-----|---------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                           | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /api/Notification/email/milestone  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.get.asset.topics (aims at endpoint [GET /api/Ticket/topics](https://api.bruin.com/index.html#/Ticket/get_api_Ticket_topics))
|     | Condition                                                 | Decision                     | Decision                         |
|-----|-----------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request           | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Ticket/topics  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.subscribe.user (aims at endpoint [POST /api/Ticket/{ticket_id}/subscribeUser](https://api.bruin.com/index.html#/Ticket/post_api_Ticket__ticketId__subscribeUser))
|     | Condition                                                                     | Decision                     | Decision                         |
|-----|-------------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                               | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /api/Ticket/{ticket_id}/subscribeUser  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.email.status (aims at endpoint [POST /api/Email/status](https://api.bruin.com/index.html#/Email/post_api_Email_status))
|     | Condition                                                 | Decision                     | Decision                         |
|-----|-----------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request           | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /api/Email/status  | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: bruin.email.reply (aims at endpoint [GET /api/Notification/email/ReplyAll](https://api.bruin.com/index.html#/Notification/post_api_Notification_email_ReplyAll))
|     | Condition                                                               | Decision                     | Decision                         |
|-----|-------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                         | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from GET /api/Notification/email/ReplyAll  | HTTP response has status 200 | HTTP response has NOT status 200 |

## Event Descriptions
### Subject: bruin.ticket.request
* [get_tickets](../services/bruin-bridge/actions/get_tickets.md)

### Subject: bruin.ticket.basic.request
* [get_tickets_basic_info](../services/bruin-bridge/actions/get_tickets_basic_info.md)

### Subject: bruin.get.site
* [get_site](../services/bruin-bridge/actions/get_site.md)

### Subject: bruin.change.ticket.severity
* [change_ticket_severity](../services/bruin-bridge/actions/change_ticket_severity.md)

### Subject: bruin.single_ticket.basic.request
* [get_single_ticket_basic_info](../services/bruin-bridge/actions/get_single_ticket_basic_info.md)

### Subject: bruin.ticket.details.request
* [get_ticket_details](../services/bruin-bridge/actions/get_ticket_details.md)

### Subject: bruin.ticket.overview.request
* [get_ticket_overview](../services/bruin-bridge/actions/get_ticket_overview.md)

### Subject: bruin.ticket.note.append.request
* [post_note](../services/bruin-bridge/actions/post_note.md)

### Subject: bruin.ticket.multiple.notes.append.request
* [post_multiple_note](../services/bruin-bridge/actions/post_multiple_notes.md)

### Subject: bruin.ticket.creation.request
* [post_ticket](../services/bruin-bridge/actions/post_ticket.md)

### Subject: bruin.ticket.status.open
* [open_ticket](../services/bruin-bridge/actions/open_ticket.md)

### Subject: bruin.ticket.status.resolve
* [resolve_ticket](../services/bruin-bridge/actions/resolve_ticket.md)

### Subject: bruin.inventory.attributes.serial
* [get_attributes_serial](../services/bruin-bridge/actions/get_attributes_serial.md)

### Subject: bruin.inventory.management.status
* [get_management_status](../services/bruin-bridge/actions/get_management_status.md)

### Subject: bruin.ticket.creation.outage.request
* [post_outage_ticket](../services/bruin-bridge/actions/post_outage_ticket.md)

### Subject: bruin.customer.get.info
* [get_client_info](../services/bruin-bridge/actions/get_client_info.md)

### Subject: bruin.customer.get.info_by_did
* [get_client_info_by_did](../services/bruin-bridge/actions/get_client_info_by_did.md)

### Subject: bruin.ticket.change.work
* [change_detail_work_queue](../services/bruin-bridge/actions/change_detail_work_queue.md)

### Subject: bruin.ticket.get.task.history
* [get_ticket_task_history](../services/bruin-bridge/actions/get_ticket_task_history.md)

### Subject: bruin.ticket.detail.get.next.results
* [get_next_results_for_ticket_details](../services/bruin-bridge/actions/get_next_results_for_ticket_detail.md)

### Subject: bruin.ticket.unpause
* [unpause_ticket](../services/bruin-bridge/actions/unpause_ticket.md)

### Subject: bruin.email.tag.request
* [post_email_tag](../services/bruin-bridge/actions/post_email_tag.md)

### Subject: bruin.get.circuit.id
* [get_circuit_id](../services/bruin-bridge/actions/get_circuit_id.md)

### Subject: bruin.mark.email.done
* [mark_email_as_done](../services/bruin-bridge/actions/mark_email_as_done.md)

### Subject: bruin.link.ticket.email
* [link_ticket_to_email](../services/bruin-bridge/actions/link_ticket_to_email.md)

### Subject: bruin.notification.email.milestone
* [post_notification_email_milestone](../services/bruin-bridge/actions/post_notification_email_milestone.md)

### Subject: bruin.get.asset.topics
* [get_asset_topics](../services/bruin-bridge/actions/get_asset_topics.md)

### Subject: bruin.subscribe.user
* [subscribe_user](../services/bruin-bridge/actions/subscribe_user.md)

### Subject: bruin.email.status
* [post_email_status](../services/bruin-bridge/actions/post_email_status.md)

### Subject: bruin.email.reply
* [post_email_reply](../services/bruin-bridge/actions/post_email_reply.md)
