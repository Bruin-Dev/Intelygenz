{{/*
Expand the name of the chart.
*/}}
{{- define "last-contact-report.name" -}}
{{- default "last-contact-report" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "last-contact-report.fullname" -}}
{{- $name := default "last-contact-report" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "last-contact-report.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "last-contact-report.labels" -}}
helm.sh/chart: {{ include "last-contact-report.chart" . }}
{{ include "last-contact-report.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: last-contact-report
microservice-type: case-of-use
environment-name: {{ .Values.global.environment }}
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "last-contact-report.selectorLabels" -}}
app.kubernetes.io/name: {{ include "last-contact-report.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of customer-cache
*/}}
{{- define "last-contact-report.configmapName" -}}
{{ include "last-contact-report.fullname" . }}-configmap
{{- end }}