# private DNS to access REDIS from kubernetes cluster
resource "aws_route53_record" "automation-mongo-private-name" {
  zone_id = data.aws_route53_zone.mettel-automation-private-zone.zone_id
  name = "ticket-collector-docdb.${local.automation-private-zone-Name}"
  type = "CNAME"
  ttl = "300"
  records = [aws_docdb_cluster.docdb[0].endpoint]
}