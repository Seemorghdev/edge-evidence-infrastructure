{{- define "edge-evidence.namespace" -}}
{{- default .Release.Namespace .Values.namespaceOverride -}}
{{- end -}}
