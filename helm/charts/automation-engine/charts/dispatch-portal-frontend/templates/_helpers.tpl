{{/*
Expand the name of the chart.
*/}}
{{- define "dispatch-portal-frontend.name" -}}
{{- default "dispatch-portal-frontend" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "dispatch-portal-frontend.fullname" -}}
{{- $name := default "dispatch-portal-frontend" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "dispatch-portal-frontend.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "dispatch-portal-frontend.labels" -}}
helm.sh/chart: {{ include "dispatch-portal-frontend.chart" . }}
{{ include "dispatch-portal-frontend.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: dispatch-portal-frontend
microservice-type: case-of-use
environment-name: {{ .Values.global.environment }}
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "dispatch-portal-frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "dispatch-portal-frontend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}