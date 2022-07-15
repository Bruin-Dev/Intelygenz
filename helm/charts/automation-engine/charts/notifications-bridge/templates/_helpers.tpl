{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "notifications-bridge.name" -}}
{{- default "notifications-bridge"| trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "notifications-bridge.fullname" -}}
{{- $name := default "notifications-bridge" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "notifications-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "notifications-bridge.labels" -}}
helm.sh/chart: {{ include "notifications-bridge.chart" . }}
{{ include "notifications-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: notifications-bridge
microservice-type: capability
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "notifications-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "notifications-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of notifications-bridge
*/}}
{{- define "notifications-bridge.configmapName" -}}
{{ include "notifications-bridge.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of notifications-bridge
*/}}
{{- define "notifications-bridge.secretName" -}}
{{ include "notifications-bridge.fullname" . }}-secret
{{- end }}