output "workflow" {
  description = "Synthetic workflow identity from the reusable module."
  value       = module.private_workflow.workflow
}

output "invoker_target_count" {
  description = "Number of synthetic target identities in the example."
  value       = module.private_workflow.invoker_target_count
}
