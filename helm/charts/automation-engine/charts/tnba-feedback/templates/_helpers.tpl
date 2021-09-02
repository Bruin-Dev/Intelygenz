{{/*
Expand the name of the chart.
*/}}
{{- define "tnba-feedback.name" -}}
{{- default "tnba-feedback" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "tnba-feedback.fullname" -}}
{{- $name := default "tnba-feedback" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "tnba-feedback.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "tnba-feedback.labels" -}}
helm.sh/chart: {{ include "tnba-feedback.chart" . }}
{{ include "tnba-feedback.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: tnba-feedback
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "tnba-feedback.selectorLabels" -}}
app.kubernetes.io/name: {{ include "tnba-feedback.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of tnba-monitor
*/}}
{{- define "tnba-feedback.configmapName" -}}
{{ include "tnba-feedback.fullname" . }}-configmap
{{- end }}