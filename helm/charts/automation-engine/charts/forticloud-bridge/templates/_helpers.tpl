{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "forticloud-bridge.name" -}}
{{- default "forticloud-bridge" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "forticloud-bridge.fullname" -}}
{{- $name := default "forticloud-bridge" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "forticloud-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "forticloud-bridge.labels" -}}
helm.sh/chart: {{ include "forticloud-bridge.chart" . }}
{{ include "forticloud-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: forticloud-bridge
microservice-type: capability
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "forticloud-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "forticloud-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of forticloud-bridge
*/}}
{{- define "forticloud-bridge.configmapName" -}}
{{ include "forticloud-bridge.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of forticloud-bridge
*/}}
{{- define "forticloud-bridge.secretName" -}}
{{ include "forticloud-bridge.fullname" . }}-secret
{{- end }}
