{{/*
Expand the name of the chart.
*/}}
{{- define "task-dispatcher.name" -}}
{{- default "task-dispatcher" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "task-dispatcher.fullname" -}}
{{- $name := default "task-dispatcher" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "task-dispatcher.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "task-dispatcher.labels" -}}
helm.sh/chart: {{ include "task-dispatcher.chart" . }}
{{ include "task-dispatcher.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: task-dispatcher
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "task-dispatcher.selectorLabels" -}}
app.kubernetes.io/name: {{ include "task-dispatcher.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of task-dispatcher
*/}}
{{- define "task-dispatcher.configmapName" -}}
{{ include "task-dispatcher.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of task-dispatcher
*/}}
{{- define "task-dispatcher.secretName" -}}
{{ include "task-dispatcher.fullname" . }}-secret
{{- end }}
