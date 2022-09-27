{{/*
Expand the name of the chart.
*/}}
{{- define "forticloud-cache.name" -}}
{{- default "forticloud-cache" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "forticloud-cache.fullname" -}}
{{- $name := default "forticloud-cache" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "forticloud-cache.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "forticloud-cache.labels" -}}
helm.sh/chart: {{ include "forticloud-cache.chart" . }}
{{ include "forticloud-cache.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: forticloud-cache
microservice-type: case-of-use
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "forticloud-cache.selectorLabels" -}}
app.kubernetes.io/name: {{ include "forticloud-cache.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of forticloud-cache
*/}}
{{- define "forticloud-cache.configmapName" -}}
{{ include "forticloud-cache.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of forticloud-cache
*/}}
{{- define "forticloud-cache.secretName" -}}
{{ include "forticloud-cache.fullname" . }}-secret
{{- end }}