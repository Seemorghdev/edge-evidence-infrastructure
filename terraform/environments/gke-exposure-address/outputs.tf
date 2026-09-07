output "address_name" {
  description = "Configured global address resource name."
  value       = google_compute_global_address.this.name
}

output "address" {
  description = "Provider-computed or caller-specified global IPv4 address."
  value       = google_compute_global_address.this.address
}
