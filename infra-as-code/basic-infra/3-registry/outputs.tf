output "KUBERNETES_RELOADER_IMAGE_URL" {
  description = "SSH keys of EKS."
  value       = aws_ecr_repository.eks_reloader.repository_url
  sensitive   = true
}
