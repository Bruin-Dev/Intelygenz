{{/*
Expand the name of the chart.
*/}}
{{- define "fraud-monitor.name" -}}
{{- default "fraud-monitor" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "fraud-monitor.fullname" -}}
{{- $name := default "fraud-monitor" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "fraud-monitor.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "fraud-monitor.labels" -}}
helm.sh/chart: {{ include "fraud-monitor.chart" . }}
{{ include "fraud-monitor.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: fraud-monitor
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "fraud-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "fraud-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of fraud-monitor
*/}}
{{- define "fraud-monitor.configmapName" -}}
{{ include "fraud-monitor.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of fraud-monitor
*/}}
{{- define "fraud-monitor.secretName" -}}
{{ include "fraud-monitor.fullname" . }}-secret
{{- end }}