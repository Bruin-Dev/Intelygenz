{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "fluent-bit-custom.name" -}}
{{- default "fluent-bit" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "fluent-bit-custom.fullname" -}}
{{- $name := default "fluent-bit" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "fluent-bit-custom.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "fluent-bit-custom.labels" -}}
helm.sh/chart: {{ include "fluent-bit-custom.chart" . }}
{{ include "fluent-bit-custom.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "fluent-bit-custom.selectorLabels" -}}
app.kubernetes.io/name: {{ include "fluent-bit-custom.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "fluent-bit-custom.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "fluent-bit-custom.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Configmap name of bruin-bridge
*/}}
{{- define "fluent-bit-custom.configmapName" -}}
{{ include "fluent-bit-custom.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of bruin-bridge
*/}}
{{- define "fluent-bit-custom.secretName" -}}
{{ include "fluent-bit-custom.fullname" . }}-secret
{{- end }}