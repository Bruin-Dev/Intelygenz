{{/*
Expand the name of the chart.
*/}}
{{- define "email-tagger-monitor.name" -}}
{{- default "email-tagger-monitor" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "email-tagger-monitor.fullname" -}}
{{- $name := default "email-tagger-monitor" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "email-tagger-monitor.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "email-tagger-monitor.labels" -}}
helm.sh/chart: {{ include "email-tagger-monitor.chart" . }}
{{ include "email-tagger-monitor.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: email-tagger-monitor
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "email-tagger-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "email-tagger-monitor.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of email-tagger-monitor
*/}}
{{- define "email-tagger-monitor.configmapName" -}}
{{ include "email-tagger-monitor.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of email-tagger-monitor
*/}}
{{- define "email-tagger-monitor.secretName" -}}
{{ include "email-tagger-monitor.fullname" . }}-secret
{{- end }}