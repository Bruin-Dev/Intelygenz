{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.          hawkeye-customer-cache
*/}}
{{- define "servicenow-bridge.name" -}}
{{- default "servicenow-bridge"| trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "servicenow-bridge.fullname" -}}
{{- $name := default "servicenow-bridge" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "servicenow-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "servicenow-bridge.labels" -}}
helm.sh/chart: {{ include "servicenow-bridge.chart" . }}
{{ include "servicenow-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: servicenow-bridge
microservice-type: capability
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "servicenow-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "servicenow-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of servicenow-bridge
*/}}
{{- define "servicenow-bridge.configmapName" -}}
{{ include "servicenow-bridge.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of servicenow-bridge
*/}}
{{- define "servicenow-bridge.secretName" -}}
{{ include "servicenow-bridge.fullname" . }}-secret
{{- end }}