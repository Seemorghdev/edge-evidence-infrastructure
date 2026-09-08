#!/usr/bin/env bash
set -Eeuo pipefail

resource_report() {
  local label="$1"
  echo "== Resource report: ${label} =="
  df -h / || true
  free -h || true
}

on_error() {
  local status="$1"
  local command="$2"
  trap - ERR
  echo "FAILED_COMMAND=${command}" >&2
  echo "FAILED_STATUS=${status}" >&2
  resource_report "failure"
  exit "$status"
}

trap 'on_error "$?" "$BASH_COMMAND"' ERR

phase_kubernetes() {
  echo "== Helm and Kustomize offline rendering =="
  docker run --rm --entrypoint helm -v "$PWD:/work" -w /work \
    alpine/helm:3.21.4 lint helm-chart/edge-evidence-platform
  docker run --rm --entrypoint helm -v "$PWD:/work" -w /work \
    alpine/helm:3.21.4 template infrastructure-review helm-chart/edge-evidence-platform \
    >/tmp/helm-rendered.yaml
  test -s /tmp/helm-rendered.yaml

  for surface in base overlays/observability; do
    local output="/tmp/kustomize-${surface//\//-}.yaml"
    docker run --rm --entrypoint kustomize -v "$PWD:/work" -w /work \
      registry.k8s.io/kustomize/kustomize:v5.8.1 build \
      --load-restrictor LoadRestrictionsNone "kustomize/${surface}" \
      >"${output}"
    test -s "${output}"
  done

  rm -f /tmp/helm-rendered.yaml /tmp/kustomize-*.yaml
}

phase_terraform() {
  echo "== Credential-free Terraform format, init, validate, and native tests =="
  terraform fmt -check -recursive

  local environments=(
    terraform/environments/gke-autopilot
    terraform/environments/cloud-run-service-example
    terraform/environments/gke-exposure-address
    terraform/environments/github-ops-wif
    terraform/environments/private-cloud-run-workflow-example
  )
  for environment in "${environments[@]}"; do
    terraform -chdir="${environment}" init -backend=false -input=false -lockfile=readonly
    terraform -chdir="${environment}" validate
    terraform -chdir="${environment}" test -no-color
  done

  local modules=(
    terraform/modules/cloud-run-service
    terraform/modules/private-cloud-run-workflow
  )
  for module in "${modules[@]}"; do
    terraform -chdir="${module}" init -backend=false -input=false
    terraform -chdir="${module}" validate
    terraform -chdir="${module}" test -no-color
  done

  resource_report "finish"
}

case "${1:-all}" in
  kubernetes) phase_kubernetes ;;
  terraform) phase_terraform ;;
  all)
    phase_kubernetes
    phase_terraform
    ;;
  *)
    echo "usage: $0 {all|kubernetes|terraform}" >&2
    exit 2
    ;;
esac
