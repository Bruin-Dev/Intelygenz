{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "dispatch-portal-backend.name" -}}
{{- default "dispatch-portal-backend" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "dispatch-portal-backend.fullname" -}}
{{- $name := default "dispatch-portal-backend" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "dispatch-portal-backend.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "dispatch-portal-backend.labels" -}}
helm.sh/chart: {{ include "dispatch-portal-backend.chart" . }}
{{ include "dispatch-portal-backend.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: dispatch-portal-backend
microservice-type: case-of-use
environment-name: {{ .Values.global.environment }}
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "dispatch-portal-backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "dispatch-portal-backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of dispatch-portal-backend
*/}}
{{- define "dispatch-portal-backend.configmapName" -}}
{{ include "dispatch-portal-backend.fullname" . }}-configmap
{{- end }}