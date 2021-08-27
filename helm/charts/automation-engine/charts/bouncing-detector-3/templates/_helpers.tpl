{{/*
Expand the name of the chart.
*/}}
{{- define "bouncing-detector-3.name" -}}
{{- default "bouncing-detector-3" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "bouncing-detector-3.fullname" -}}
{{- $name := default "bouncing-detector-3" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "bouncing-detector-3.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "bouncing-detector-3.labels" -}}
helm.sh/chart: {{ include "bouncing-detector-3.chart" . }}
{{ include "bouncing-detector-3.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: bouncing-detector-3
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "bouncing-detector-3.selectorLabels" -}}
app.kubernetes.io/name: {{ include "bouncing-detector-3.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of bouncing-detector-3
*/}}
{{- define "bouncing-detector-3.configmapName" -}}
{{ include "bouncing-detector-3.fullname" . }}-configmap
{{- end }}