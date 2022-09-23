{{/*
Expand the name of the chart.
*/}}
{{- define "forticloud-monitor.name" -}}
{{- default "forticloud-monitor" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "forticloud-monitor.fullname" -}}
{{- $name := default "forticloud-monitor" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "forticloud-monitor.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "forticloud-monitor.labels" -}}
helm.sh/chart: {{ include "forticloud-monitor.chart" . }}
{{ include "forticloud-monitor.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: forticloud-monitor
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "forticloud-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "forticloud-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of forticloud-monitor
*/}}
{{- define "forticloud-monitor.configmapName" -}}
{{ include "forticloud-monitor.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of forticloud-monitor
*/}}
{{- define "forticloud-monitor.secretName" -}}
{{ include "forticloud-monitor.fullname" . }}-secret
{{- end }}