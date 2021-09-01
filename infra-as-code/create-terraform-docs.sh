#!/bin/bash

for i in $(find . -mindepth 1 -maxdepth 1 -type d | sort | sed 's|^./||' || exit 1); do
    (
        cd "${i}" || exit
        if [[ ${i} != "kre" && ${i} != "basic-infra" && ${i} != "elasticaches" && ${i} != "kre-runtimes" ]]; then
          echo "Generating terraform-doc in file ${i}/README.md"
          terraform-docs markdown . > README.md
        fi
        if [[ ${i} != "data-collector" ]]; then
            for j in $(find . -mindepth 1 -maxdepth 1 -type d | sort | sed 's|^./||' || exit 1); do
                (
                  cd "${j}" || exit
                  if [[ ${j} != "modules" && ${j} != "runtimes" ]]; then
                    echo "Generating terraform-doc in file ${j}/README.md"
                    terraform-docs markdown . > README.md
                  else
                    for k in $(find . -mindepth 1 -maxdepth 1 -type d | sort | sed 's|^./||' || exit 1); do
                      (
                        cd "${k}" || exit 1
                        echo "Generating terraform-doc in file ${k}/README.md"
                        terraform-docs markdown . > README.md
                        cd ..
                      )
                    done
                  fi
                  cd ..
                )
            done
        fi
    )
done