{{/*
Expand the name of the chart.
*/}}
{{- define "digi-bridge.name" -}}
{{- default "digi-bridge" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "digi-bridge.fullname" -}}
{{- $name := default "digi-bridge" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "digi-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "digi-bridge.labels" -}}
helm.sh/chart: {{ include "digi-bridge.chart" . }}
{{ include "digi-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
project: mettel-automation
component: bruin-bridge
microservice-type: capability
environment-name: {{ .Values.global.environment }}
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "digi-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "digi-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of digi-bridge
*/}}
{{- define "digi-bridge.configmapName" -}}
{{ include "digi-bridge.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of bruin-bridge
*/}}
{{- define "digi-bridge.secretName" -}}
{{ include "digi-bridge.fullname" . }}-secret
{{- end }}