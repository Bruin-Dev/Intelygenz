resource "aws_ssm_parameter" "parameter-forticloud-cache-time-to-refresh-interval" {
    name        = "/automation-engine/${local.env}/forticloud-cache/time-to-refresh-interval"
    description = "Time to refresh the Forticloud cache "
    type        = "SecureString"
    value       = "-"  # to edit go to parameter store dashboard.
    key_id      =  aws_kms_alias.kms_key.name

    lifecycle {
        ignore_changes = [
            value,
        ]
    }

    tags = merge(var.common_info, {
        Name = "TIME_TO_REFRESH_INTERVAL"
        note = "can be updated from the parameter store dashboard"
    })
}
resource "aws_ssm_parameter" "parameter-forticloud-cache-monitorable-management-status" {
    name = "/automation-engine/${local.env}/forticloud-cache/monitorable-management-status"
    description = "Managements statuses to store devices in cache "
    type = "SecureString"
    value = "-"
    # to edit go to parameter store dashboard.
    key_id = aws_kms_alias.kms_key.name

    lifecycle {
        ignore_changes = [
            value,
        ]
    }

    tags = merge(var.common_info, {
        Name = "MONITORABLE_MANAGEMENT_STATUSES"
        note = "can be updated from the parameter store dashboard"
    })
}