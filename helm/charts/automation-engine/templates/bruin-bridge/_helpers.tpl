{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.          hawkeye-customer-cache
*/}}
{{- define "bruin-bridge.name" -}}
{{- default "bruin-bridge"| trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "bruin-bridge.fullname" -}}
{{- $name := default "bruin-bridge" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "bruin-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "bruin-bridge.labels" -}}
helm.sh/chart: {{ include "bruin-bridge.chart" . }}
{{ include "bruin-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: bruin-bridge
microservice-type: capability
environment-name: {{ .Values.config.environment_name }}
current-environment: {{ .Values.config.environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "bruin-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "bruin-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}