{{/*
Expand the name of the chart.
*/}}
{{- define "repair-tickets-monitor.name" -}}
{{- default "repair-tickets-monitor" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "repair-tickets-monitor.fullname" -}}
{{- $name := default "repair-tickets-monitor" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "repair-tickets-monitor.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "repair-tickets-monitor.labels" -}}
helm.sh/chart: {{ include "repair-tickets-monitor.chart" . }}
{{ include "repair-tickets-monitor.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: repair-tickets-monitor
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "repair-tickets-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "repair-tickets-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of repair-tickets-monitor
*/}}
{{- define "repair-tickets-monitor.configmapName" -}}
{{ include "repair-tickets-monitor.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of repair-tickets-monitor
*/}}
{{- define "repair-tickets-monitor.secretName" -}}
{{ include "repair-tickets-monitor.fullname" . }}-secret
{{- end }}