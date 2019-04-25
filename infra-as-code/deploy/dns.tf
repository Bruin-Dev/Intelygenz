data "aws_route53_zone" "mettel" {
  name = "mettel-automation.com."
}

resource "aws_route53_record" "mettel-automation-pro" {
  zone_id = "${data.aws_route53_zone.mettel.zone_id}"
  name = "${var.subdomain}.${data.aws_route53_zone.mettel.name}"
  type = "A"

  alias {
    name = "${aws_alb.mettel-automation-pro-alb.dns_name}"
    zone_id = "${aws_alb.mettel-automation-pro-alb.zone_id}"
    evaluate_target_health = true
  }
}
