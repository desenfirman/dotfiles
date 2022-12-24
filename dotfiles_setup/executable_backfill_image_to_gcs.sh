#!/bin/bash

d=2019-01-01
until [[ $d > 2021-01-01 ]]; do
  cur_date=$d
  next_date=$(date -d "$d + 1 month")
  y=$(date -d "$cur_date" "+%Y")
  m=$(date -d "$cur_date" "+%m")
  next_y=$(date -d "$next_date" "+%Y")
  next_m=$(date -d "$next_date" "+%m")
  echo "Processing data for year-month $y-$m to $next_y-$next_m"
  rclone -P copy --ignore-existing --min-age "$next_y-$next_m-01T00:00:00Z" --max-age "$y-$m-01T00:00:00Z"  apps-ellenka-net:/home/ellenkan/web/apps.ellenka.net/public_html/ellenkan/public/picture/monitoring/ lnk-dw-bucket:lnk-dw-bucket/environment=prod/dag_scope=non-airflow/dag_id=fibersquad-object-detection/domain=product_monitoring/year=$y/month=$m/
  echo "Successfully processing data for year-month $y-$m"
  d=$(date -I -d "$d + 1 month")
done


