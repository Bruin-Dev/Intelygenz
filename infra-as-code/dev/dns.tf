//data "aws_route53_zone" "automation" {
//  name = "mettel-automation.net."
//}
//
//resource "aws_route53_record" "automation" {
//  zone_id = "${data.aws_route53_zone.automation.zone_id}"
//  name = "${var.SUBDOMAIN}.${data.aws_route53_zone.automation.name}"
//  type = "A"
//
//  alias {
//    name = "${aws_alb.automation-alb.dns_name}"
//    zone_id = "${aws_alb.automation-alb.zone_id}"
//    evaluate_target_health = true
//  }
//}

resource "aws_service_discovery_private_dns_namespace" "automation-zone" {
  name        = "${var.ENVIRONMENT}.local"
  description = "private DNS zone for automation"
  vpc         = "${aws_vpc.automation-vpc.id}"
}
