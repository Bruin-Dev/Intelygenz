{{/*
Expand the name of the chart.
*/}}
{{- define "service-affecting-monitor.name" -}}
{{- default "sam" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "service-affecting-monitor.fullname" -}}
{{- $name := default "sam" }}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "service-affecting-monitor.Chart" -}}
{{- printf "%s-%s" $.Chart.Name $.Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "service-affecting-monitor.labels" -}}
helm.sh/chart: {{ include "service-affecting-monitor.Chart" $ }}
{{ include "service-affecting-monitor.selectorLabels" $ }}
{{- if $.Chart.AppVersion }}
app.kubernetes.io/version: {{ $.Chart.AppVersion | quote }}
{{- end }}
project: mettel-automation
microservice-type: case-of-use
environment-name: "{{ $.Values.global.environment }}"
current-environment: {{ $.Values.global.current_environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "service-affecting-monitor.selectorLabels" -}}
app.kubernetes.io/name: {{ include "service-affecting-monitor.name" $ }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}