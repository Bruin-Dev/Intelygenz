{{/*
Expand the name of the chart.
*/}}
{{- define "digi-reboot-report.name" -}}
{{- default "digi-reboot-report" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "digi-reboot-report.fullname" -}}
{{- $name := default "digi-reboot-report" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "digi-reboot-report.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "digi-reboot-report.labels" -}}
helm.sh/chart: {{ include "digi-reboot-report.chart" . }}
{{ include "digi-reboot-report.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: digi-reboot-report
microservice-type: case-of-use
environment-name: {{ .Values.global.environment }}
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "digi-reboot-report.selectorLabels" -}}
app.kubernetes.io/name: {{ include "digi-reboot-report.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of customer-cache
*/}}
{{- define "digi-reboot-report.configmapName" -}}
{{ include "digi-reboot-report.fullname" . }}-configmap
{{- end }}