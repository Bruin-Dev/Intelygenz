{{/*
Expand the name of the chart.
*/}}
{{- define "tnba-monitor.name" -}}
{{- default "tnba-monitor" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "tnba-monitor.fullname" -}}
{{- $name := default "tnba-monitor" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "tnba-monitor.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "tnba-monitor.labels" -}}
helm.sh/chart: {{ include "tnba-monitor.chart" . }}
{{ include "tnba-monitor.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: tnba-monitor
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "tnba-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "tnba-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of tnba-monitor
*/}}
{{- define "tnba-monitor.configmapName" -}}
{{ include "tnba-monitor.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of tnba-monitor
*/}}
{{- define "tnba-monitor.secretName" -}}
{{ include "tnba-monitor.fullname" . }}-secret
{{- end }}