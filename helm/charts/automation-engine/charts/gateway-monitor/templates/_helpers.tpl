{{/*
Expand the name of the chart.
*/}}
{{- define "gateway-monitor.name" -}}
{{- default "gateway-monitor" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "gateway-monitor.fullname" -}}
{{- $name := default "gateway-monitor" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "gateway-monitor.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "gateway-monitor.labels" -}}
helm.sh/chart: {{ include "gateway-monitor.chart" . }}
{{ include "gateway-monitor.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: gateway-monitor
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "gateway-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "gateway-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of gateway-monitor
*/}}
{{- define "gateway-monitor.configmapName" -}}
{{ include "gateway-monitor.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of gateway-monitor
*/}}
{{- define "gateway-monitor.secretName" -}}
{{ include "gateway-monitor.fullname" . }}-secret
{{- end }}
