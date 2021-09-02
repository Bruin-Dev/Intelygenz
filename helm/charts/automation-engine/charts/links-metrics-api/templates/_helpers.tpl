{{/*
Expand the name of the chart.
*/}}
{{- define "links-metrics-api.name" -}}
{{- default "links-metrics-api" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "links-metrics-api.fullname" -}}
{{- $name := default "links-metrics-api" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "links-metrics-api.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "links-metrics-api.labels" -}}
helm.sh/chart: {{ include "links-metrics-api.chart" . }}
{{ include "links-metrics-api.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: links-metrics-api
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "links-metrics-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "links-metrics-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of links-metrics-api
*/}}
{{- define "links-metrics-api.configmapName" -}}
{{ include "links-metrics-api.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of links-metrics-api
*/}}
{{- define "links-metrics-api.secretName" -}}
{{ include "links-metrics-api.fullname" . }}-secret
{{- end }}
