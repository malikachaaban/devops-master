output "master_ip" { value = azurerm_public_ip.master.ip_address }
output "worker_ip"  { value = azurerm_public_ip.worker.ip_address }
output "ssh_key_path" { value = "${path.module}/devops-key.pem" }
