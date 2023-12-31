{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "t7-bridge.name" -}}
{{- default "t7-bridge" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "t7-bridge.fullname" -}}
{{- $name := default "t7-bridge" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "t7-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "t7-bridge.labels" -}}
helm.sh/chart: {{ include "t7-bridge.chart" . }}
{{ include "t7-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: t7-bridge
microservice-type: capability
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "t7-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "t7-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of t7-bridge
*/}}
{{- define "t7-bridge.configmapName" -}}
{{ include "t7-bridge.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of t7-bridge
*/}}
{{- define "t7-bridge.secretName" -}}
{{ include "t7-bridge.fullname" . }}-secret
{{- end }}