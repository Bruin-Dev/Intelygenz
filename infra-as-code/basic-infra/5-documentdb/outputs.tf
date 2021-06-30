# This outputs have custom definition because can be empty and terraform will not fail:
# https://github.com/hashicorp/terraform/issues/23222

output "ticket-collector-mongo-host" {
  value = join("", aws_docdb_cluster.docdb.*.endpoint)
}
