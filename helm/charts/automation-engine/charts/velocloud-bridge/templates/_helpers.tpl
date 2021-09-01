{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "velocloud-bridge.name" -}}
{{- default "velocloud-bridge" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "velocloud-bridge.fullname" -}}
{{- $name := default "velocloud-bridge" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "velocloud-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "velocloud-bridge.labels" -}}
helm.sh/chart: {{ include "velocloud-bridge.chart" . }}
{{ include "velocloud-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: velocloud-bridge
microservice-type: capability
environment-name: {{ .Values.global.environment }}
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "velocloud-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "velocloud-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of velocloud-bridge
*/}}
{{- define "velocloud-bridge.configmapName" -}}
{{ include "velocloud-bridge.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of velocloud-bridge
*/}}
{{- define "velocloud-bridge.secretName" -}}
{{ include "velocloud-bridge.fullname" . }}-secret
{{- end }}
