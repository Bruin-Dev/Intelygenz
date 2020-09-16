{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "notifier.name" -}}
{{- default "notifier"| trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "notifier.fullname" -}}
{{- $name := default "notifier" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "notifier.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "notifier.labels" -}}
helm.sh/chart: {{ include "notifier.chart" . }}
{{ include "notifier.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: notifier
microservice-type: capability
environment-name: {{ .Values.global.environment }}
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "notifier.selectorLabels" -}}
app.kubernetes.io/name: {{ include "notifier.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of notifier
*/}}
{{- define "notifier.configmapName" -}}
{{ include "notifier.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of notifier
*/}}
{{- define "notifier.secretName" -}}
{{ include "notifier.fullname" . }}-secret
{{- end }}