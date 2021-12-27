{{/*
Expand the name of the chart.
*/}}
{{- define "email-tagger-kre-bridge.name" -}}
{{- default "email-tagger-kre-bridge" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "email-tagger-kre-bridge.fullname" -}}
{{- $name := default "email-tagger-kre-bridge" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "email-tagger-kre-bridge.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "email-tagger-kre-bridge.labels" -}}
helm.sh/chart: {{ include "email-tagger-kre-bridge.chart" . }}
{{ include "email-tagger-kre-bridge.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
component: email-tagger-kre-bridge
microservice-type: capability
environment-name: "{{ .Values.global.environment }}"
current-environment: {{ .Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "email-tagger-kre-bridge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "email-tagger-kre-bridge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Configmap name of email-tagger-kre-bridge
*/}}
{{- define "email-tagger-kre-bridge.configmapName" -}}
{{ include "email-tagger-kre-bridge.fullname" . }}-configmap
{{- end }}

{{/*
Secret name of email-tagger-kre-bridge
*/}}
{{- define "email-tagger-kre-bridge.secretName" -}}
{{ include "email-tagger-kre-bridge.fullname" . }}-secret
{{- end }}