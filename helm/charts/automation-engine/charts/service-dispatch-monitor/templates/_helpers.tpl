{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "service-dispatch-monitor.name" -}}
{{- default "service-dispatch-monitor" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "service-dispatch-monitor.fullname" -}}
{{- $name := default "service-dispatch-monitor" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "service-dispatch-monitor.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "service-dispatch-monitor.labels" -}}
helm.sh/chart: {{ include "service-dispatch-monitor.chart" . }}
{{ include "service-dispatch-monitor.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: service-dispatch-monitor
microservice-type: case-of-use
environment-name: {{ .Values.global.environment }}
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "service-dispatch-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "service-dispatch-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of service-dispatch-monitor
*/}}
{{- define "service-dispatch-monitor.configmapName" -}}
{{ include "service-dispatch-monitor.fullname" . }}-configmap
{{- end }}