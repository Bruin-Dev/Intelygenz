{{/*
Expand the name of the chart.
*/}}
{{- define "ticket-collector.name" -}}
{{- default "ticket-collector" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "ticket-collector.fullname" -}}
{{- $name := default "ticket-collector" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ticket-collector.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ticket-collector.labels" -}}
helm.sh/chart: {{ include "ticket-collector.chart" . }}
{{ include "ticket-collector.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: ticket-collector
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ticket-collector.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ticket-collector.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of ticket-collector
*/}}
{{- define "ticket-collector.configmapName" -}}
{{ include "ticket-collector.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of ticket-collector
*/}}
{{- define "ticket-collector.secretName" -}}
{{ include "ticket-collector.fullname" . }}-secret
{{- end }}
