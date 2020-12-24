{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "cts-bridge.name" -}}
{{- default .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "cts-bridge.fullname" -}}
{{- $name := default .Chart.Name }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "cts-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "cts-bridge.labels" -}}
helm.sh/chart: {{ include "cts-bridge.chart" . }}
{{ include "cts-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: cts-bridge
microservice-type: capability
environment-name: {{ .Values.config.environment_name }}
current-environment: {{ .Values.config.environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "cts-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cts-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
