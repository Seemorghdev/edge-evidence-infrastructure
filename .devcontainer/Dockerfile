FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

ARG TERRAFORM_VERSION=1.9.8
ARG TERRAFORM_LINUX_AMD64_SHA256=186e0145f5e5f2eb97cbd785bc78f21bae4ef15119349f6ad4fa535b83b10df8
ARG TERRAFORM_LINUX_ARM64_SHA256=f85868798834558239f6148834884008f2722548f84034c9b0f62934b2d73ebb

RUN set -eux; \
    rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/sources.list.d/yarn.sources; \
    command -v curl; \
    command -v unzip; \
    command -v sha256sum; \
    arch="$(dpkg --print-architecture)"; \
    case "${arch}" in \
      amd64) terraform_sha256="${TERRAFORM_LINUX_AMD64_SHA256}" ;; \
      arm64) terraform_sha256="${TERRAFORM_LINUX_ARM64_SHA256}" ;; \
      *) echo "unsupported evaluator architecture: ${arch}" >&2; exit 1 ;; \
    esac; \
    terraform_zip="terraform_${TERRAFORM_VERSION}_linux_${arch}.zip"; \
    curl -fsSLo "/tmp/${terraform_zip}" "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/${terraform_zip}"; \
    echo "${terraform_sha256}  /tmp/${terraform_zip}" | sha256sum -c -; \
    unzip "/tmp/${terraform_zip}" -d /usr/local/bin; \
    rm -f "/tmp/${terraform_zip}"; \
    terraform version | head -n 1 | grep -Fx "Terraform v${TERRAFORM_VERSION}"; \
    python -m pip install --no-cache-dir "PyYAML>=6,<7" "pytest>=8,<9"
