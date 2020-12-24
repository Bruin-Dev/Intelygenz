{{/*
Expand the name of the chart.
*/}}
{{- define "lumin-billing-report.name" -}}
{{- default .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "lumin-billing-report.fullname" -}}
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
{{- define "lumin-billing-report.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "lumin-billing-report.labels" -}}
helm.sh/chart: {{ include "lumin-billing-report.chart" . }}
{{ include "lumin-billing-report.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: lumin-billing-report
microservice-type: independent
environment-name: {{ .Values.config.environment_name }}
current-environment: {{ .Values.config.environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "lumin-billing-report.selectorLabels" -}}
app.kubernetes.io/name: {{ include "lumin-billing-report.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
