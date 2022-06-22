{{/*
Expand the name of the chart.
*/}}
{{- define "velocloud-gateway-monitor.name" -}}
{{- default "velocloud-gateway-monitor" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "velocloud-gateway-monitor.fullname" -}}
{{- $name := default "velocloud-gateway-monitor" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "velocloud-gateway-monitor.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "velocloud-gateway-monitor.labels" -}}
helm.sh/chart: {{ include "velocloud-gateway-monitor.chart" . }}
{{ include "velocloud-gateway-monitor.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: velocloud-gateway-monitor
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "velocloud-gateway-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "velocloud-gateway-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of velocloud-gateway-monitor
*/}}
{{- define "velocloud-gateway-monitor.configmapName" -}}
{{ include "velocloud-gateway-monitor.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of velocloud-gateway-monitor
*/}}
{{- define "velocloud-gateway-monitor.secretName" -}}
{{ include "velocloud-gateway-monitor.fullname" . }}-secret
{{- end }}
