{{- define "bloodbridge.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "bloodbridge.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else if contains (include "bloodbridge.name" .) .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name (include "bloodbridge.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{/* Common labels. Usage: include "bloodbridge.labels" (dict "ctx" . "component" "backend") */}}
{{- define "bloodbridge.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .ctx.Chart.Name .ctx.Chart.Version }}
app.kubernetes.io/part-of: bloodbridge
app.kubernetes.io/managed-by: {{ .ctx.Release.Service }}
app.kubernetes.io/version: {{ .ctx.Chart.AppVersion | quote }}
{{ include "bloodbridge.selectorLabels" . }}
{{- end -}}

{{- define "bloodbridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "bloodbridge.name" .ctx }}
app.kubernetes.io/instance: {{ .ctx.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end -}}

{{- define "bloodbridge.image" -}}
{{- printf "%s:%s" .image.repository (default .ctx.Chart.AppVersion .image.tag) -}}
{{- end -}}

{{- define "bloodbridge.dbSecret" -}}
{{- default (printf "%s-db" (include "bloodbridge.fullname" .)) .Values.postgres.existingSecret -}}
{{- end -}}

{{- define "bloodbridge.dbHost" -}}
{{- default (printf "%s-postgres" (include "bloodbridge.fullname" .)) .Values.postgres.host -}}
{{- end -}}

{{- define "bloodbridge.backendUrl" -}}
{{- printf "%s-backend:8000" (include "bloodbridge.fullname" .) -}}
{{- end -}}

{{/* Hardened container settings shared by every workload (Pod Security "restricted" compliant). */}}
{{- define "bloodbridge.containerSecurity" -}}
allowPrivilegeEscalation: false
readOnlyRootFilesystem: true
capabilities:
  drop: ["ALL"]
{{- end -}}
