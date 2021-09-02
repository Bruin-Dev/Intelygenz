{{/*
Expand the name of the chart.
*/}}
{{- define "links-metrics-collector.name" -}}
{{- default "links-metrics-collector" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "links-metrics-collector.fullname" -}}
{{- $name := default "links-metrics-collector" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "links-metrics-collector.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "links-metrics-collector.labels" -}}
helm.sh/chart: {{ include "links-metrics-collector.chart" . }}
{{ include "links-metrics-collector.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: links-metrics-collector
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "links-metrics-collector.selectorLabels" -}}
app.kubernetes.io/name: {{ include "links-metrics-collector.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of links-metrics-collector
*/}}
{{- define "links-metrics-collector.configmapName" -}}
{{ include "links-metrics-collector.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of links-metrics-collector
*/}}
{{- define "links-metrics-collector.secretName" -}}
{{ include "links-metrics-collector.fullname" . }}-secret
{{- end }}
