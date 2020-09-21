resource "aws_ses_email_identity" "email_identities" {
  count = length(var.igz_users_email)
  email = var.igz_users_email[count.index]
}