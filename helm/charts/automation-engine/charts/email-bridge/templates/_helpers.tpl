{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "email-bridge.name" -}}
{{- default "email-bridge"| trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "email-bridge.fullname" -}}
{{- $name := default "email-bridge" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "email-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "email-bridge.labels" -}}
helm.sh/chart: {{ include "email-bridge.chart" . }}
{{ include "email-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: email-bridge
microservice-type: capability
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "email-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "email-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of email-bridge
*/}}
{{- define "email-bridge.configmapName" -}}
{{ include "email-bridge.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of email-bridge
*/}}
{{- define "email-bridge.secretName" -}}
{{ include "email-bridge.fullname" . }}-secret
{{- end }}