{{/*
Expand the name of the chart.
*/}}
{{- define "bouncing-detector-2.name" -}}
{{- default "bouncing-detector-2" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "bouncing-detector-2.fullname" -}}
{{- $name := default "bouncing-detector-2" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "bouncing-detector-2.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "bouncing-detector-2.labels" -}}
helm.sh/chart: {{ include "bouncing-detector-2.chart" . }}
{{ include "bouncing-detector-2.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: bouncing-detector-2
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "bouncing-detector-2.selectorLabels" -}}
app.kubernetes.io/name: {{ include "bouncing-detector-2.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of bouncing-detector-2
*/}}
{{- define "bouncing-detector-2.configmapName" -}}
{{ include "bouncing-detector-2.fullname" . }}-configmap
{{- end }}