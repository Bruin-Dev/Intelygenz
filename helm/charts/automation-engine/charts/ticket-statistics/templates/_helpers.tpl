{{/*
Expand the name of the chart.
*/}}
{{- define "ticket-statistics.name" -}}
{{- default "ticket-statistics" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "ticket-statistics.fullname" -}}
{{- $name := default "ticket-statistics" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ticket-statistics.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ticket-statistics.labels" -}}
helm.sh/chart: {{ include "ticket-statistics.chart" . }}
{{ include "ticket-statistics.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: ticket-statistics
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ticket-statistics.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ticket-statistics.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of ticket-statistics
*/}}
{{- define "ticket-statistics.configmapName" -}}
{{ include "ticket-statistics.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of ticket-statistics
*/}}
{{- define "ticket-statistics.secretName" -}}
{{ include "ticket-statistics.fullname" . }}-secret
{{- end }}
