resource "aws_waf_web_acl" "waf" {
  name        = "${var.prefix}-website-${var.environment}-waf"
  metric_name = "${var.prefix}websitewaf"

  default_action {
    type = "ALLOW"
  }

  rules {
    action {
      type = "BLOCK"
    }

    priority = 10
    rule_id  = aws_waf_rule.detect_vpn_access.id
    type     = "REGULAR"
  }
}

resource "aws_waf_rule" "detect_vpn_access" {
  name        = "${var.prefix}detectvpnaccess"
  metric_name = "${var.prefix}detectvpnaccess"

  predicates {
    data_id = aws_waf_ipset.vpn_remote_ipset.id
    negated = true
    type    = "IPMatch"
  }
}

resource "aws_waf_ipset" "vpn_remote_ipset" {
  name = "${var.prefix}matchvpnremoteip"

  dynamic "ip_set_descriptors" {
    for_each = [for ip_set in var.vpn_remote_ipset : {
      type  = ip_set.type
      value = ip_set.value
    }]
    content {
      type  = ip_set_descriptors.value.type
      value = ip_set_descriptors.value.value
    }
  }
}
