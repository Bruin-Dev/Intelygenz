---
hide:
  - navigation
  - toc
---

# Repair tickets monitor

## Process Workflows
![[](../../images/20-repair-tickets-monitor.jpg)](../../images/20-repair-tickets-monitor.jpg)

## List of Decisions made by the Repair tickets monitor
### new_closed_tickets_feedback
|     | Condition                                     | Decision                                                    | Decision                                                                                   |
|-----|-----------------------------------------------|-------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| 1   | Get status and cancellation reason from bruin | Successfully got status and cancellation reason from bruin  | Error with getting status and cancellation reason from bruin (response status is not 200)  |

### new_created_tickets_feedback

|     | Condition                                              | Decision                                           | Decision                          | Decision                                                                  |
|-----|--------------------------------------------------------|----------------------------------------------------|-----------------------------------|---------------------------------------------------------------------------|
| 1   | Get single ticket info with service number from bruin  | status response from bruin is in range 200 and 300 | status response from bruin is 404 | status response from bruin is not in range of 200 and 300 and is not 404  |

|     | Condition                                              | Decision                                             | Decision                                            |
|-----|--------------------------------------------------------|------------------------------------------------------|-----------------------------------------------------|
| 2   | Build sitemap                                          | site map created                                     | site map is empty                                   |
| 3   | Save created ticket feedback to RTA                    | response from RTA is in range of 200 and 300         | response from RTA is NOT in range of 200 and 300    |

### repair_tickets_monitor
|     | Condition                                              | Decision                        | Decision                       |
|-----|--------------------------------------------------------|---------------------------------|--------------------------------|
| 1   | Split emails by repair tag emails and other tag emails | Email list that have repair tag | Email list that have other tag |
| 2   | Get email inference                                    | Got email inference             | Failed to get email inference  |
| 3   | Try and get valid service numbers site map             | No ResponseException raise      | ResponseException raised       |

|     | Condition                                                           | Decision            | Decision                                                                 | Decision                                                             |
|-----|---------------------------------------------------------------------|---------------------|--------------------------------------------------------------------------|----------------------------------------------------------------------|
| 4   | Determining actionable and inference_data["predicted_class"] values | actionable is true  | actionable is false and inference_data["predicted_class"] is not"Other"  | actionable is false and inference_data["predicted_class"] is "Other" |

|     | Condition                                                                                                           | Decision                                                                                    | Decision                                                                             |
|-----|---------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| 5   | Determining allowed_service_number_site_map size and is_ticket_actionable value                                     | allowed_service_number_site_map is empty and is_ticket_actionable is true                   | allowed_service_number_site_map is not empty or is_ticket_actionable is false        |
| 6   | Determining allowed_service_number_site_map size and if a ticket can update or is updated                           | allowed_service_number_site_map is empty and no tickets could be updated or updated         | allowed_service_number_site_map is not empty or  tickets could be updated or updated |
| 7   | Determining the type of email, actionable value, amount of validated tickets, and if we can send an autoreply       | if email is a parent email, actionable, no validated tickets, and can send an auto reply    | if email is a reply email                                                            |
| 8   | Determining if at least one ticket has been created or updated, and there if there is no cancellations in any site  | at least one ticket has been created or updated, and there is no cancellations in any site  | No ticket has been created or updated, or there is a cancellations in any site       |

## Event Descriptions
### new_closed_tickets_feedback
* [start_closed_ticket_feedback](../services/repair-tickets-monitor/actions/new_closed_tickets_feedback/start_closed_ticket_feedback.md)

### new_created_tickets_feedback
* [start_created_ticket_feedback](../services/repair-tickets-monitor/actions/new_created_tickets_feedback/start_created_ticket_feedback.md)

### reprocess_old_parent_emails
* [start_old_parent_email_reprocess](../services/repair-tickets-monitor/actions/reprocess_old_parent_emails/start_old_parent_email_reprocess.md)

### repair_tickets_monitor
* [start_repair_tickets_monitor](../services/repair-tickets-monitor/actions/repair_tickets_monitor/start_repair_tickets_monitor.md)