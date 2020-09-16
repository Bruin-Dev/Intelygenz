{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "lit-bridge.name" -}}
{{- default "lit-bridge" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "lit-bridge.fullname" -}}
{{- $name := default "lit-bridge" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "lit-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "lit-bridge.labels" -}}
helm.sh/chart: {{ include "lit-bridge.chart" . }}
{{ include "lit-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: lit-bridge
microservice-type: capability
environment-name: {{ .Values.global.environment }}
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "lit-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "lit-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of bruin-bridge
*/}}
{{- define "lit-bridge.configmapName" -}}
{{ include "lit-bridge.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of bruin-bridge
*/}}
{{- define "lit-bridge.secretName" -}}
{{ include "lit-bridge.fullname" . }}-secret
{{- end }}